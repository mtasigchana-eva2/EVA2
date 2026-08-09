from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.lista_sedes,
        name="lista_sedes"
    ),

    path(
        "nuevo/",
        views.nueva_sede,
        name="nueva_sede"
    ),

    path(
        "editar/<int:id>/",
        views.editar_sede,
        name="editar_sede"
    ),

    path(
        "eliminar/<int:id>/",
        views.eliminar_sede,
        name="eliminar_sede"
    ),

]