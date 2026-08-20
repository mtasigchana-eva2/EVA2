from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.lista_solicitudes_herramientas,
        name="lista_solicitudes_herramientas",
    ),

    path(
        "nuevo/",
        views.nueva_solicitud_herramienta,
        name="nueva_solicitud_herramienta",
    ),

    path(
        "editar/<int:id>/",
        views.editar_solicitud_herramienta,
        name="editar_solicitud_herramienta",
    ),

    path(
        "aprobar/<int:id>/",
        views.aprobar_solicitud_herramienta,
        name="aprobar_solicitud_herramienta",
    ),

    path(
        "rechazar/<int:id>/",
        views.rechazar_solicitud_herramienta,
        name="rechazar_solicitud_herramienta",
    ),

    path(
        "eliminar/<int:id>/",
        views.eliminar_solicitud_herramienta,
        name="eliminar_solicitud_herramienta",
    ),

    path(
        "devolver/<int:id>/",
        views.devolver_herramienta,
        name="devolver_herramienta",
    ),

    path(
        "pdf/<int:id>/",
        views.exportar_pdf_solicitud_herramienta,
        name="exportar_pdf_solicitud_herramienta",
    ),
]