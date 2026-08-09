from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.models import Perfil
from .forms import PerfilForm


def lista_usuarios(request):

    perfiles = Perfil.objects.select_related(
        "usuario",
        "carrera",
        "sede",
    )

    buscar = request.GET.get("buscar")

    if buscar:
        perfiles = perfiles.filter(
            usuario__username__icontains=buscar
        )

    return render(
        request,
        "gestion_usuarios/index.html",
        {
            "perfiles": perfiles,
            "buscar": buscar,
        }
    )


def editar_usuario(request, id):

    perfil = get_object_or_404(
        Perfil,
        id=id
    )

    if request.method == "POST":

        formulario = PerfilForm(
            request.POST,
            instance=perfil
        )

        if formulario.is_valid():

            formulario.save()

            messages.success(
                request,
                "Usuario actualizado correctamente."
            )

            return redirect("lista_usuarios")

    else:

        formulario = PerfilForm(
            instance=perfil
        )

    return render(
        request,
        "gestion_usuarios/editar.html",
        {
            "formulario": formulario,
            "perfil": perfil,
        }
    )


def eliminar_usuario(request, id):

    perfil = get_object_or_404(
        Perfil,
        id=id
    )

    if request.method == "POST":

        perfil.usuario.delete()

        messages.success(
            request,
            "Usuario eliminado correctamente."
        )

        return redirect("lista_usuarios")

    return render(
        request,
        "gestion_usuarios/eliminar.html",
        {
            "perfil": perfil
        }
    )