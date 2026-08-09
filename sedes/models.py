from django.db import models


class Sede(models.Model):

    nombre = models.CharField(
        max_length=120,
        unique=True
    )

    ciudad = models.CharField(
        max_length=100
    )

    direccion = models.CharField(
        max_length=200
    )

    telefono = models.CharField(
        max_length=20,
        blank=True
    )

    estado = models.BooleanField(
        default=True
    )

    def __str__(self):

        return self.nombre