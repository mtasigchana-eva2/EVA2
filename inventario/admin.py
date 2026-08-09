from django.contrib import admin
from .models import Inventario


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):

    list_display = (

        "codigo",
        "nombre",
        "categoria",
        "carrera",
        "sede",
        "cantidad",
        "estado",

    )

    search_fields = (

        "codigo",
        "nombre",

    )

    list_filter = (

        "estado",
        "carrera",
        "sede",

    )