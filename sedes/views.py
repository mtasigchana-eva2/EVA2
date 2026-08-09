from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from .models import Sede
from .forms import SedeForm


def lista_sedes(request):

    buscar = request.GET.get("buscar", "")

    sedes = Sede.objects.all()

    if buscar:

        sedes = sedes.filter(

            Q(nombre__icontains=buscar) |
            Q(ciudad__icontains=buscar) |
            Q(direccion__icontains=buscar)

        )

    return render(
        request,
        "sedes/lista.html",
        {
            "sedes": sedes,
            "buscar": buscar,
        }
    )


def nueva_sede(request):

    if request.method == "POST":

        formulario = SedeForm(request.POST)

        if formulario.is_valid():

            formulario.save()

            return redirect("lista_sedes")

    else:

        formulario = SedeForm()

    return render(
        request,
        "sedes/nuevo.html",
        {
            "formulario": formulario
        }
    )


def editar_sede(request, id):

    sede = get_object_or_404(Sede, id=id)

    if request.method == "POST":

        formulario = SedeForm(
            request.POST,
            instance=sede
        )

        if formulario.is_valid():

            formulario.save()

            return redirect("lista_sedes")

    else:

        formulario = SedeForm(instance=sede)

    return render(
        request,
        "sedes/editar.html",
        {
            "formulario": formulario,
            "sede": sede
        }
    )


def eliminar_sede(request, id):

    sede = get_object_or_404(
        Sede,
        id=id
    )

    sede.delete()

    return redirect("lista_sedes")