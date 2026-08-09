from django.contrib import admin
from .models import Solicitud


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "estudiante",
        "laboratorio",
        "fecha",
        "estado",
    )

    list_filter = (
        "estado",
        "fecha",
    )

    search_fields = (
        "estudiante__username",
        "docente",
    )