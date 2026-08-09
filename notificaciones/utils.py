from django.core.mail import send_mail
from django.conf import settings
from .models import Notificacion

def enviar_notificacion_y_correo(usuario, titulo, mensaje, url_destino=""):
    """
    1. Crea la notificación interna (Campanita).
    2. Envía un correo electrónico si el usuario tiene email registrado.
    """
    if not usuario:
        return

    # 1. Crear Notificación Interna
    Notificacion.objects.create(
        usuario=usuario,
        titulo=titulo,
        mensaje=mensaje,
        url_destino=url_destino
    )

    # 2. Enviar Correo SMTP
    if usuario.email:
        try:
            send_mail(
                subject=f"[EVA2] {titulo}",
                message=mensaje,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                recipient_list=[usuario.email],
                fail_silently=True,  # Para que no detenga el flujo si falle el servidor SMTP
            )
        except Exception as e:
            print(f"Error al enviar correo: {e}")