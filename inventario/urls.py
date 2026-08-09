from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.lista_inventario,
        name="lista_inventario"
    ),

    path(
        "nuevo/",
        views.crear_inventario,
        name="nuevo_inventario"
    ),

    path(
        "editar/<int:id>/",
        views.editar_inventario,
        name="editar_inventario"
    ),

    path(
        "eliminar/<int:id>/",
        views.eliminar_inventario,
        name="eliminar_inventario"
    ),

]