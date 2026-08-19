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

    # Cantidad total registrada en esta sede
    cantidad = models.PositiveIntegerField(
        default=1
    )

    # Cantidad actualmente prestada
    cantidad_prestada = models.PositiveIntegerField(
        default=0
    )

    # Cantidad actualmente en mantenimiento
    cantidad_mantenimiento = models.PositiveIntegerField(
        default=0
    )

    # Cantidad registrada como dañada
    cantidad_danada = models.PositiveIntegerField(
        default=0
    )

    estado = models.CharField(
        max_length=30,
        choices=ESTADOS,
        default="Disponible"
    )

    observacion = models.TextField(
        blank=True
    )

    @property
    def cantidad_disponible(self):
        """
        Calcula automáticamente las unidades disponibles.
        """
        disponible = (
            self.cantidad
            - self.cantidad_prestada
            - self.cantidad_mantenimiento
            - self.cantidad_danada
        )

        return max(disponible, 0)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"