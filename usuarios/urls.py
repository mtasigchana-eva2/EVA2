from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("logout/", views.cerrar_sesion, name="logout"),

    path("registro/", views.registro, name="registro"),

    path("perfil/", views.perfil, name="perfil"),

    # ==========================================
    # ACCESOS TEMPORALES PARA DEMOSTRACIÓN TESIS
    # ==========================================

    path(
        "demo/TESIS-XAVIER-2026-8K4M/",
        views.demo_estudiante,
        name="demo_estudiante"
    ),

    path(
        "demo/TESIS-CARLA-2026-9P7Q/",
        views.demo_superadministrador,
        name="demo_superadministrador"
    ),
]