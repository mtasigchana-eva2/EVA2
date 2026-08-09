from django.db import models
from inventario.models import Inventario


class Herramienta(models.Model):

    ESTADOS = [
        ("Disponible", "Disponible"),
        ("Prestada", "Prestada"),
        ("Mantenimiento", "Mantenimiento"),
        ("Dañada", "Dañada"),
    ]

    inventario = models.ForeignKey(
        Inventario,
        on_delete=models.CASCADE
    )

    codigo = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    numero_serie = models.CharField(
        max_length=50,
        unique=True
    )

    marca = models.CharField(
        max_length=100
    )

    modelo = models.CharField(
        max_length=100,
        blank=True
    )

    estado = models.CharField(
        max_length=30,
        choices=ESTADOS,
        default="Disponible"
    )

    observacion = models.TextField(
        blank=True
    )

    def __str__(self):
        if self.codigo:
            return f"{self.codigo} - {self.numero_serie}"
        return self.numero_serie