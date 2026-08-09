from django.db import models
from django.contrib.auth.models import User

from carreras.models import Carrera
from sedes.models import Sede


class Solicitud(models.Model):

    ESTADOS = [
        ("Pendiente", "Pendiente"),
        ("Aprobada", "Aprobada"),
        ("Rechazada", "Rechazada"),
    ]

    estudiante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="solicitudes_laboratorio"
    )

    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.CASCADE
    )

    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE
    )

    # Se cambia de ForeignKey a CharField para eliminar la dependencia de la app laboratorios
    laboratorio = models.CharField(
        max_length=150
    )

    docente = models.CharField(
        max_length=150
    )

    fecha = models.DateField()

    hora_inicio = models.TimeField()

    hora_fin = models.TimeField()

    motivo = models.TextField()

    documento = models.FileField(
        upload_to="solicitudes_laboratorio/",
        blank=True,
        null=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="Pendiente"
    )

    aprobado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="laboratorios_aprobados"
    )

    fecha_respuesta = models.DateTimeField(
        blank=True,
        null=True
    )

    observacion = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.estudiante.username} - {self.laboratorio}"