from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.lista_herramientas,
        name="lista_herramientas"
    ),

    path(
        "nuevo/",
        views.nueva_herramienta,
        name="nueva_herramienta"
    ),

    path(
        "editar/<int:id>/",
        views.editar_herramienta,
        name="editar_herramienta"
    ),

    path(
        "eliminar/<int:id>/",
        views.eliminar_herramienta,
        name="eliminar_herramienta"
    ),

]