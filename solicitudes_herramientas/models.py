from django.db import models
from herramientas.models import Herramienta


class SolicitudHerramienta(models.Model):

    ESTADOS = [

        ("Pendiente", "Pendiente"),
        ("Aprobada", "Aprobada"),
        ("Rechazada", "Rechazada"),
        ("Devuelta", "Devuelta"),

    ]

    estudiante = models.CharField(
        max_length=150
    )

    carrera = models.CharField(
        max_length=150
    )

    profesor = models.CharField(
        max_length=150
    )

    herramienta = models.ForeignKey(
        Herramienta,
        on_delete=models.CASCADE
    )

    cantidad = models.PositiveIntegerField()

    fecha_inicio = models.DateField()

    fecha_fin = models.DateField()

    motivo = models.TextField()

    documento = models.FileField(
        upload_to="permisos_herramientas/",
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
        return f"{self.estudiante} - {self.herramienta}"