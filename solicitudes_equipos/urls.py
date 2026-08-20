from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.lista_solicitudes_equipos,
        name="lista_solicitudes_equipos"
    ),

    path(
        "nuevo/",
        views.nueva_solicitud_equipo,
        name="nueva_solicitud_equipo"
    ),

    path(
        "editar/<int:id>/",
        views.editar_solicitud_equipo,
        name="editar_solicitud_equipo"
    ),

    path(
        "eliminar/<int:id>/",
        views.eliminar_solicitud_equipo,
        name="eliminar_solicitud_equipo"
    ),

    path(
        "aprobar/<int:id>/",
        views.aprobar_solicitud_equipo,
        name="aprobar_solicitud_equipo"
    ),

    path(
        "rechazar/<int:id>/",
        views.rechazar_solicitud_equipo,
        name="rechazar_solicitud_equipo"
    ),

    path(
        "devolver/<int:id>/",
        views.devolver_solicitud_equipo,
        name="devolver_solicitud_equipo"
    ),

    path(
        "pdf/<int:id>/",
        views.exportar_pdf_solicitud_equipo,
        name="exportar_pdf_solicitud_equipo"
    ),
]