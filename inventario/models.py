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

    # Cantidad total registrada para este equipo
    # en esta sede.
    cantidad = models.PositiveIntegerField(
        default=1
    )

    # Cantidad actualmente prestada.
    cantidad_prestada = models.PositiveIntegerField(
        default=0
    )

    # Cantidad actualmente en mantenimiento.
    cantidad_mantenimiento = models.PositiveIntegerField(
        default=0
    )

    # Cantidad actualmente dañada.
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

        Ejemplo:
        Total = 10
        Prestadas = 1
        Mantenimiento = 0
        Dañadas = 0

        Disponible = 9
        """

        disponible = (
            self.cantidad
            - self.cantidad_prestada
            - self.cantidad_mantenimiento
            - self.cantidad_danada
        )

        return max(disponible, 0)

    def actualizar_estado(self):
        """
        Actualiza automáticamente el estado general
        dependiendo de las cantidades actuales.
        """

        if self.cantidad_disponible > 0:
            self.estado = "Disponible"

        elif self.cantidad_prestada > 0:
            self.estado = "Prestado"

        elif self.cantidad_mantenimiento > 0:
            self.estado = "Mantenimiento"

        elif self.cantidad_danada > 0:
            self.estado = "Dañado"

        else:
            self.estado = "Disponible"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"