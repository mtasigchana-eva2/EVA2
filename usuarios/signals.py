from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        from usuarios.models import Perfil

        rol = "Superadministrador" if instance.is_superuser else "Estudiante"

        Perfil.objects.create(
            usuario=instance,
            rol=rol,
            estado="Activo"
        )


@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    if hasattr(instance, "perfil"):
        instance.perfil.save()