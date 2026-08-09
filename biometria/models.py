from django.db import models
from django.contrib.auth.models import User


class Biometria(models.Model):

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    foto = models.ImageField(
        upload_to="biometria/"
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    activo = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.usuario.username