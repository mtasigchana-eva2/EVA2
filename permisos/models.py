from django.db import models


class Permiso(models.Model):

    ESTADOS = [

        ("Pendiente", "Pendiente"),
        ("Aprobado", "Aprobado"),
        ("Rechazado", "Rechazado"),

    ]

    estudiante = models.CharField(
        max_length=150
    )

    carrera = models.CharField(
        max_length=100
    )

    docente = models.CharField(
        max_length=150
    )

    fecha_inicio = models.DateField()

    fecha_fin = models.DateField()

    motivo = models.TextField()

    documento = models.FileField(
        upload_to="permisos/",
        blank=True,
        null=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="Pendiente"
    )

    fecha_solicitud = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.estudiante