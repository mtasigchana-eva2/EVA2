from django.db import models

from carreras.models import Carrera
from sedes.models import Sede


class Inventario(models.Model):

    ESTADOS = [

        ("Disponible", "Disponible"),
        ("Prestado", "Prestado"),
        ("Mantenimiento", "Mantenimiento"),
        ("Dañado", "Dañado"),

    ]

    codigo = models.CharField(
        max_length=20,
        unique=True
    )

    nombre = models.CharField(
        max_length=150
    )

    categoria = models.CharField(
        max_length=100
    )

    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.CASCADE
    )

    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE
    )

    cantidad = models.PositiveIntegerField(
        default=1
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
        return f"{self.codigo} - {self.nombre}"