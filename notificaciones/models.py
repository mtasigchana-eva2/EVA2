from django.db import models
from django.contrib.auth.models import User

class Notificacion(models.Model):
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="notificaciones"
    )
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    url_destino = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Notificación para {self.usuario.username} - {self.titulo}"