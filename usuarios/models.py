from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):

    # ==========================
    # ROLES DEL SISTEMA
    # ==========================
    ROLES = [
        ("Superadministrador", "Superadministrador"),
        ("Administrador Talleres", "Administrador de Talleres o Laboratorio"),
        ("Coordinador Carrera", "Coordinador de Carrera"),
        ("Coordinador Talleres", "Coordinador de Talleres y Laboratorio"),
        ("Docente", "Docente"),
        ("Estudiante", "Estudiante"),
    ]

    # ==========================
    # ESTADOS DEL USUARIO
    # ==========================
    ESTADOS = [
        ("Activo", "Activo"),
        ("Inactivo", "Inactivo"),
    ]

    # ==========================
    # DATOS DEL PERFIL
    # ==========================
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil"
    )

    foto = models.ImageField(
        upload_to="perfiles/",
        blank=True,
        null=True
    )

    rol = models.CharField(
        max_length=50,
        choices=ROLES,
        default="Estudiante"
    )

    carrera = models.ForeignKey(
        "carreras.Carrera",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    sede = models.ForeignKey(
        "sedes.Sede",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    telefono = models.CharField(
        max_length=20,
        blank=True
    )

    fecha_nacimiento = models.DateField(
        blank=True,
        null=True
    )

    edad = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    direccion = models.CharField(
        max_length=250,
        blank=True
    )

    descripcion = models.CharField(
        max_length=250,
        blank=True,
        help_text="Observaciones o cargo adicional del usuario."
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="Activo"
    )

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} - {self.rol}"