from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_notificaciones, name='lista_notificaciones'),
    path('leida/<int:id>/', views.marcar_como_leida, name='marcar_como_leida'),
    path('marcar-todas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
]