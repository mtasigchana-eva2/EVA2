from django.db import models
from inventario.models import Inventario


class SolicitudEquipo(models.Model):

    ESTADOS = [
        ("Pendiente", "Pendiente"),
        ("Aprobada", "Aprobada"),
        ("Rechazada", "Rechazada"),
        ("Devuelta", "Devuelta"),
    ]

    estudiante = models.CharField(max_length=150)

    carrera = models.CharField(max_length=150)

    profesor = models.CharField(max_length=150)

    equipo = models.ForeignKey(
        Inventario,
        on_delete=models.CASCADE
    )

    cantidad = models.PositiveIntegerField(default=1)

    numero_equipo = models.CharField(
        max_length=50,
        blank=True
    )

    numero_serie = models.CharField(
        max_length=100,
        blank=True
    )

    fecha_inicio = models.DateField()

    fecha_fin = models.DateField()

    motivo = models.TextField()

    documento = models.FileField(
        upload_to="solicitudes_equipos/",
        blank=True,
        null=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="Pendiente"
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.estudiante} - {self.equipo}"