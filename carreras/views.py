from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .forms import CarreraForm
from .models import Carrera


def lista_carreras(request):

    buscar = request.GET.get("buscar", "")

    carreras = Carrera.objects.all()

    if buscar:
        carreras = carreras.filter(
            nombre__icontains=buscar
        )

    return render(
        request,
        "carreras/lista.html",
        {
            "carreras": carreras,
            "buscar": buscar,
        }
    )


def nueva_carrera(request):

    if request.method == "POST":

        formulario = CarreraForm(request.POST)

        if formulario.is_valid():

            formulario.save()

            messages.success(
                request,
                "Carrera registrada correctamente."
            )

            return redirect("lista_carreras")

    else:

        formulario = CarreraForm()

    return render(
        request,
        "carreras/nuevo.html",
        {
            "formulario": formulario
        }
    )


def editar_carrera(request, id):

    carrera = get_object_or_404(
        Carrera,
        id=id
    )

    if request.method == "POST":

        formulario = CarreraForm(
            request.POST,
            instance=carrera
        )

        if formulario.is_valid():

            formulario.save()

            messages.success(
                request,
                "Carrera actualizada correctamente."
            )

            return redirect("lista_carreras")

    else:

        formulario = CarreraForm(
            instance=carrera
        )

    return render(
        request,
        "carreras/editar.html",
        {
            "formulario": formulario,
            "carrera": carrera
        }
    )


def eliminar_carrera(request, id):

    carrera = get_object_or_404(
        Carrera,
        id=id
    )

    carrera.delete()

    messages.success(
        request,
        "Carrera eliminada correctamente."
    )

    return redirect("lista_carreras")