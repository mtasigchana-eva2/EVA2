from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    # Administración por defecto de Django
    path("admin/", admin.site.urls),

    # Aplicaciones del Sistema EVA2
    path("", include("usuarios.urls")),
    path("usuarios-admin/", include("gestion_usuarios.urls")),
    path("carreras/", include("carreras.urls")),
    path("sedes/", include("sedes.urls")),
    path("solicitudes/", include("solicitudes.urls")),
    path("solicitudes-herramientas/", include("solicitudes_herramientas.urls")),
    path("solicitudes-equipos/", include("solicitudes_equipos.urls")),
    path("inventario/", include("inventario.urls")),
    path("herramientas/", include("herramientas.urls")),
    path("reportes/", include("reportes.urls")),
    path("permisos/", include("permisos.urls")),
    path("biometria/", include("biometria.urls")),
    path("notificaciones/", include("notificaciones.urls")),

    # ==========================================
    # RECUPERACIÓN DE CONTRASEÑA
    # ==========================================

    path(
        "recuperar-contrasena/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            success_url="/recuperar-contrasena/enviado/"
        ),
        name="password_reset",
    ),

    path(
        "recuperar-contrasena/enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),

    path(
        "recuperar-contrasena/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url="/recuperar-contrasena/completado/"
        ),
        name="password_reset_confirm",
    ),

    path(
        "recuperar-contrasena/completado/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )