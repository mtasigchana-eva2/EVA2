from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import InventarioForm
from .models import Inventario
from usuarios.permisos import (
    puede_agregar_inventario,
    puede_editar_inventario,
    puede_eliminar_inventario,
)


def lista_inventario(request):

    buscar = request.GET.get("buscar", "")

    inventario = Inventario.objects.all()

    if buscar:
        inventario = inventario.filter(
            Q(codigo__icontains=buscar) |
            Q(nombre__icontains=buscar) |
            Q(categoria__icontains=buscar)
        )

    return render(
        request,
        "inventario/index.html",
        {
            "inventario": inventario,
            "buscar": buscar
        }
    )


def crear_inventario(request):

    if not puede_agregar_inventario(request.user):
        return HttpResponseForbidden(
            "No tiene permisos para agregar elementos al inventario."
        )

    if request.method == "POST":

        formulario = InventarioForm(
            request.POST,
            request.FILES or None
        )

        if formulario.is_valid():

            formulario.save()

            messages.success(
                request,
                "Equipo registrado correctamente."
            )

            return redirect("lista_inventario")

        else:  # Este es el cambio que solicitaste
            print(formulario.errors)

    else:

        formulario = InventarioForm()

    return render(
        request,
        "inventario/nuevo.html",
        {
            "formulario": formulario
        }
    )


def editar_inventario(request, id):

    if not puede_editar_inventario(request.user):
        return HttpResponseForbidden(
            "No tiene permisos para editar el inventario."
        )

    item = get_object_or_404(
        Inventario,
        id=id
    )

    if request.method == "POST":

        formulario = InventarioForm(
            request.POST,
            request.FILES or None,
            instance=item
        )

        if formulario.is_valid():

            formulario.save()

            messages.success(
                request,
                "Equipo actualizado correctamente."
            )

            return redirect("lista_inventario")
        

    else:

        formulario = InventarioForm(
            instance=item
        )

    return render(
        request,
        "inventario/nuevo.html",
        {
            "formulario": formulario,
            "item": item
        }
    )


def eliminar_inventario(request, id):

    if not puede_eliminar_inventario(request.user):
        return HttpResponseForbidden(
            "No tiene permisos para eliminar elementos."
        )

    item = get_object_or_404(
        Inventario,
        id=id
    )

    item.delete()

    messages.success(
        request,
        "Equipo eliminado correctamente."
    )

    return redirect("lista_inventario")