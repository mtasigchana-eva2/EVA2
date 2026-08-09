from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notificacion


@login_required
def lista_notificaciones(request):
    """Muestra todas las notificaciones del usuario autenticado."""
    notificaciones = Notificacion.objects.filter(usuario=request.user)
    return render(
        request,
        'notificaciones/index.html',
        {'notificaciones': notificaciones}
    )


@login_required
def marcar_como_leida(request, id):
    """Marca una notificación específica como leída y reacciona reorientando
    al enlace de destino si existe."""
    notificacion = get_object_or_404(Notificacion, id=id, usuario=request.user)
    
    if not notificacion.leido:
        notificacion.leido = True
        notificacion.save()

    if notificacion.url_destino:
        return redirect(notificacion.url_destino)

    return redirect('lista_notificaciones')


@login_required
def marcar_todas_leidas(request):
    """Marca masivamente todas las notificaciones pendientes como leídas."""
    Notificacion.objects.filter(usuario=request.user, leido=False).update(leido=True)
    return redirect('lista_notificaciones')