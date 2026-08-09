from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Importación de formularios
from .forms import RegistroUsuarioForm, UserEditarForm, PerfilEditarForm
from .models import Perfil

# Importación de modelos para el Dashboard
from carreras.models import Carrera
from sedes.models import Sede
from inventario.models import Inventario
from herramientas.models import Herramienta
from solicitudes.models import Solicitud


def registro(request):
    if request.method == "POST":
        formulario = RegistroUsuarioForm(request.POST)
        if formulario.is_valid():
            usuario = User.objects.create_user(
                username=formulario.cleaned_data["username"],
                first_name=formulario.cleaned_data["first_name"],
                last_name=formulario.cleaned_data["last_name"],
                email=formulario.cleaned_data["email"],
                password=formulario.cleaned_data["password"]
            )
            login(request, usuario)
            messages.warning(request, "⚠ Por favor, completa tu perfil institucional.")
            return redirect("perfil")
        else:
            # IMPRIME ERRORES EN LA TERMINAL PARA SABER QUÉ RECHAZÓ DJANGO
            print("--- ERROR DE VALIDACIÓN EN REGISTRO ---")
            print(formulario.errors)
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        formulario = RegistroUsuarioForm()

    return render(
        request,
        "auth/registro.html",
        {"formulario": formulario}
    )


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:
            login(request, usuario)
            return redirect("dashboard")
        else:
            messages.error(
                request,
                "Correo o contraseña incorrectos."
            )

    return render(request, "auth/login.html")


@login_required(login_url="login")
def dashboard(request):
    contexto = {
        "total_carreras": Carrera.objects.count(),
        "total_sedes": Sede.objects.count(),
        "total_inventario": Inventario.objects.count(),
        "total_herramientas": Herramienta.objects.count(),
        "total_solicitudes": Solicitud.objects.count(),
        "ultimas": Solicitud.objects.order_by("-id")[:5],
    }
    
    return render(
        request,
        "dashboard/index.html",
        contexto
    )


def cerrar_sesion(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def perfil(request):
    perfil_obj, _ = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == "POST":
        u_form = UserEditarForm(request.POST, instance=request.user)
        p_form = PerfilEditarForm(request.POST, request.FILES, instance=perfil_obj)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "¡Perfil actualizado con éxito!")
            return redirect("perfil")
    else:
        u_form = UserEditarForm(instance=request.user)
        p_form = PerfilEditarForm(instance=perfil_obj)

    perfil_incompleto = not perfil_obj.foto or not perfil_obj.telefono

    return render(
        request,
        "usuarios/perfil.html",
        {
            "u_form": u_form,
            "p_form": p_form,
            "perfil_incompleto": perfil_incompleto,
        }
    )