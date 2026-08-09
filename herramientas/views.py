from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden

from .models import Herramienta
from .forms import HerramientaForm
from usuarios.permisos import (
    puede_agregar_inventario,
    puede_editar_inventario,
    puede_eliminar_inventario,
)


def lista_herramientas(request):
    buscar = request.GET.get("buscar")
    herramientas = Herramienta.objects.all()

    if buscar:
        herramientas = herramientas.filter(
            Q(codigo__icontains=buscar) |
            Q(numero_serie__icontains=buscar) |
            Q(marca__icontains=buscar) |
            Q(modelo__icontains=buscar)
        )

    return render(
        request,
        "herramientas/index.html",
        {
            "herramientas": herramientas,
            "buscar": buscar,
        }
    )


def nueva_herramienta(request):
    if not puede_agregar_inventario(request.user):
        return HttpResponseForbidden("No tiene permisos para agregar herramientas al inventario.")

    if request.method == "POST":
        formulario = HerramientaForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(
                request,
                "Herramienta registrada correctamente."
            )
            return redirect("lista_herramientas")
    else:
        formulario = HerramientaForm()

    return render(
        request,
        "herramientas/nuevo.html",
        {
            "formulario": formulario
        }
    )


def editar_herramienta(request, id):
    if not puede_editar_inventario(request.user):
        return HttpResponseForbidden("No tiene permisos para editar este registro.")

    herramienta = get_object_or_404(
        Herramienta,
        id=id
    )

    if request.method == "POST":
        formulario = HerramientaForm(
            request.POST,
            instance=herramienta
        )
        if formulario.is_valid():
            formulario.save()
            messages.success(
                request,
                "Herramienta actualizada correctamente."
            )
            return redirect("lista_herramientas")
    else:
        formulario = HerramientaForm(
            instance=herramienta
        )

    return render(
        request,
        "herramientas/nuevo.html",
        {
            "formulario": formulario
        }
    )


def eliminar_herramienta(request, id):
    if not puede_eliminar_inventario(request.user):
        return HttpResponseForbidden("No tiene permisos para eliminar elementos del inventario.")

    herramienta = get_object_or_404(
        Herramienta,
        id=id
    )

    herramienta.delete()

    messages.success(
        request,
        "Herramienta eliminada correctamente."
    )

    return redirect("lista_herramientas")