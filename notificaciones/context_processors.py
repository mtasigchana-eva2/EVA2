from .models import Notificacion

def notificaciones_context(request):
    if request.user.is_authenticated:
        no_leidas = Notificacion.objects.filter(
            usuario=request.user, 
            leido=False
        ).count()
        
        ultimas_notificaciones = Notificacion.objects.filter(
            usuario=request.user
        )[:5]

        return {
            'notificaciones_no_leidas_count': no_leidas,
            'ultimas_notificaciones': ultimas_notificaciones
        }
    return {
        'notificaciones_no_leidas_count': 0,
        'ultimas_notificaciones': []
    }