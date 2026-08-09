from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.lista_carreras,
        name="lista_carreras"
    ),

    path(
        "nuevo/",
        views.nueva_carrera,
        name="nueva_carrera"
    ),

    path(
        "editar/<int:id>/",
        views.editar_carrera,
        name="editar_carrera"
    ),

    path(
        "eliminar/<int:id>/",
        views.eliminar_carrera,
        name="eliminar_carrera"
    ),

]