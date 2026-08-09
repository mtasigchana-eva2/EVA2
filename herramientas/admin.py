from django.contrib import admin
from .models import Herramienta


@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):

    list_display = (
        "numero_serie",
        "inventario",
        "marca",
        "modelo",
        "estado",
    )

    search_fields = (
        "numero_serie",
        "marca",
        "modelo",
    )

    list_filter = (
        "estado",
    )