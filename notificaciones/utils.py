from django.core.mail import send_mail
from django.conf import settings
from .models import Notificacion


def enviar_notificacion_y_correo(
    usuario,
    titulo,
    mensaje,
    url_destino=""
):
    """
    Crea una notificación interna y, si es posible,
    envía también un correo electrónico.

    Los errores de notificación o correo no deben
    impedir que la operación principal continúe.
    """

    # Si no existe usuario, simplemente no hacemos nada.
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
    # 2. ENVIAR CORREO ELECTRÓNICO
    # ==========================================================

    if usuario.email:
        try:
            send_mail(
                subject=f"[SEMGA] {titulo}",
                message=mensaje,
                from_email=getattr(
                    settings,
                    "DEFAULT_FROM_EMAIL",
                    None
                ),
                recipient_list=[usuario.email],
                fail_silently=True,
            )

        except Exception as e:
            print("==========================================")
            print("ERROR AL ENVIAR CORREO")
            print(f"Usuario: {usuario}")
            print(f"Correo: {usuario.email}")
            print(f"Error: {e}")
            print("==========================================")

    # ==========================================================
    # IMPORTANTE:
    # Esta función nunca debe detener la creación
    # de la solicitud principal.
    # ==========================================================

    return