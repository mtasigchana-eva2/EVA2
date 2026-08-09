import base64
import cv2
import numpy as np
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import render

from .models import Biometria
from .utils import base64_a_imagen
from .comparador import comparar
from .procesador import preparar


def _cargar_imagen_desde_storage(foto_field):
    """
    Lee un FieldFile/ImageField de Django y lo convierte en una matriz de OpenCV (BGR/Grayscale).
    Evita fallos si se utiliza S3 o almacenamiento no local en donde `.path` no existe.
    """
    try:
        foto_field.open()
        bytes_data = foto_field.read()
        nparr = np.frombuffer(bytes_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        return img
    except Exception:
        return None


# ==========================================
# FUNCIONES DE REGISTRO
# ==========================================

@login_required
def registrar_biometria(request):
    biometria = Biometria.objects.filter(usuario=request.user).first()
    return render(
        request,
        "biometria/registrar.html",
        {"biometria": biometria}
    )


@login_required
def guardar_biometria(request):
    if request.method == "POST":
        imagen_raw = request.POST.get("imagen")
        if imagen_raw:
            # 1. Convertir Base64 a imagen OpenCV
            imagen = base64_a_imagen(imagen_raw)
            if imagen is None:
                return JsonResponse({"ok": False, "error": "No se pudo leer la imagen capturada."})

            # 2. Procesar la imagen (recorte, redimensionado 250x250, escala de grises, etc.)
            imagen_procesada = preparar(imagen)
            if imagen_procesada is None:
                return JsonResponse({"ok": False, "error": "No se detectó un rostro válido en la imagen."})

            # 3. Convertir nuevamente a PNG
            _, buffer = cv2.imencode(".png", imagen_procesada)
            archivo = ContentFile(
                buffer.tobytes(),
                name=f"{request.user.username}.png"
            )

            # 4. Obtener o crear instancia de Biometria y guardar
            biometria, _ = Biometria.objects.get_or_create(usuario=request.user)
            biometria.foto.save(
                f"{request.user.username}.png",
                archivo,
                save=True
            )

            return JsonResponse({
                "ok": True,
                "mensaje": "Biometría registrada correctamente."
            })

    return JsonResponse({
        "ok": False,
        "error": "Petición no válida o imagen no proporcionada."
    }, status=400)


# ==========================================
# FUNCIONES DE AUTENTICACIÓN Y PROCESAMIENTO
# ==========================================

@login_required
def comparar_rostro(request):
    if request.method == "POST":
        imagen_base64 = request.POST.get("imagen")
        biometria = Biometria.objects.filter(usuario=request.user).first()

        if not biometria or not biometria.foto:
            return JsonResponse({"ok": False, "error": "El usuario no tiene biometría registrada."})

        # Process standard input frame
        img_capturada = base64_a_imagen(imagen_base64)
        if img_capturada is not None:
            img_capturada = preparar(img_capturada)

        img_guardada = _cargar_imagen_desde_storage(biometria.foto)

        if img_capturada is None or img_guardada is None:
            return JsonResponse({"ok": False, "error": "Error al procesar o leer las imágenes."})

        # Comparación real
        coincide, similitud = comparar(img_capturada, img_guardada)

        return JsonResponse({
            "ok": coincide,
            "similitud": similitud
        })

    return JsonResponse({"ok": False, "error": "Método no permitido."}, status=405)


def login_biometrico(request):
    if request.method == "GET":
        return render(request, "biometria/login.html")

    if request.method == "POST":
        username = request.POST.get("username")
        imagen_base64 = request.POST.get("imagen")

        if not username or not imagen_base64:
            return JsonResponse({"ok": False, "error": "Nombre de usuario o imagen faltante."})

        try:
            user = User.objects.get(username=username)
            biometria = Biometria.objects.get(usuario=user)

            if not biometria.foto:
                return JsonResponse({"ok": False, "error": "El usuario no tiene una foto registrada."})

            # 1. Convertir la captura base64 a OpenCV
            img_capturada = base64_a_imagen(imagen_base64)
            if img_capturada is None:
                return JsonResponse({"ok": False, "error": "Error al decodificar la imagen capturada."})

            # 2. Verificación de prueba de vida (Liveness) - TEMPORALMENTE DESHABILITADO
            # vida, mensaje = verificar_vida(img_capturada)
            # if not vida:
            #     return JsonResponse({
            #         "ok": False,
            #         "error": mensaje
            #     })

            # 3. Preprocesar captura y cargar foto guardada
            img_capturada = preparar(img_capturada)
            img_guardada = _cargar_imagen_desde_storage(biometria.foto)

            if img_capturada is None or img_guardada is None:
                return JsonResponse({"ok": False, "error": "Error al procesar el rostro capturado o la imagen guardada."})

            # 4. Comparación mediante comparador.py
            es_valido, similitud = comparar(img_capturada, img_guardada)

            if es_valido:
                # Especificar el backend para evitar AttributeError en login
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                return JsonResponse({
                    "ok": True,
                    "redirect_url": "/dashboard/",
                    "similitud": similitud
                })
            else:
                return JsonResponse({"ok": False, "error": "Rostro no coincide.", "similitud": similitud})

        except (User.DoesNotExist, Biometria.DoesNotExist):
            return JsonResponse({"ok": False, "error": "Usuario o registro biométrico no encontrado."})

    return JsonResponse({"ok": False, "error": "Método no permitido."}, status=405)


def validar_rostro(request):
    if request.method == "POST":
        imagen_base64 = request.POST.get("imagen")

        if not imagen_base64:
            return JsonResponse({"ok": False, "error": "No se recibió ninguna imagen."})

        imagen = base64_a_imagen(imagen_base64)
        if imagen is None:
            return JsonResponse({"ok": False, "error": "No se pudo leer la imagen."})

        # Validar si contiene un rostro preprocesable
        imagen_procesada = preparar(imagen)
        if imagen_procesada is None:
            return JsonResponse({"ok": False, "error": "No se detectó ningún rostro en la imagen."})

        return JsonResponse({
            "ok": True,
            "mensaje": "Imagen válida y rostro detectado."
        })

    return JsonResponse({"ok": False, "error": "Método no permitido."}, status=405)


def detectar_vida(request):
    if request.method == "POST":
        # Espacio reservado para lógica de Liveness Detection vía endpoint si fuera necesario
        return JsonResponse({
            "ok": True,
            "mensaje": "Prueba de vida aprobada."
        })

    return JsonResponse({"ok": False, "error": "Método no permitido."}, status=405)