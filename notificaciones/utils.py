from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from .models import Notificacion


def enviar_notificacion_y_correo(
    usuario,
    titulo,
    mensaje,
    url_destino=""
):
    """
    Crea una notificación interna y, si el usuario tiene correo,
    intenta enviarle un correo electrónico.

    Los errores de notificación o correo NO deben impedir
    que la solicitud principal se complete.
    """

    if not usuario:
        return

    # ==========================================================
    # 1. CREAR NOTIFICACIÓN INTERNA
    # ==========================================================
    try:
        Notificacion.objects.create(
            usuario=usuario,
            titulo=titulo,
            mensaje=mensaje,
            url_destino=url_destino
        )

    except Exception as e:
        print("==========================================")
        print("ERROR AL CREAR NOTIFICACIÓN")
        print(f"Usuario: {usuario}")
        print(f"Título: {titulo}")
        print(f"Error: {e}")
        print("==========================================")

    # ==========================================================
    # 2. ENVIAR CORREO
    # ==========================================================
    if usuario.email:

        try:
            conexion = get_connection(
                backend="django.core.mail.backends.smtp.EmailBackend",
                fail_silently=True,
                timeout=5,
            )

            correo = EmailMessage(
                subject=f"[EVA2] {titulo}",
                body=mensaje,
                from_email=getattr(
                    settings,
                    "DEFAULT_FROM_EMAIL",
                    None
                ),
                to=[usuario.email],
                connection=conexion,
            )

            correo.send(fail_silently=True)

        except Exception as e:
            print("==========================================")
            print("ERROR AL ENVIAR CORREO")
            print(f"Usuario: {usuario}")
            print(f"Correo: {usuario.email}")
            print(f"Error: {e}")
            print("==========================================")