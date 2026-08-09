from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.lista_permisos,
        name="lista_permisos"
    ),

    path(
        "nuevo/",
        views.nuevo_permiso,
        name="nuevo_permiso"
    ),

    path(
        "editar/<int:id>/",
        views.editar_permiso,
        name="editar_permiso"
    ),

    path(
        "eliminar/<int:id>/",
        views.eliminar_permiso,
        name="eliminar_permiso"
    ),

    path(
        "pdf/<int:id>/",
        views.exportar_pdf_permiso,
        name="exportar_pdf_permiso"
    ),

]