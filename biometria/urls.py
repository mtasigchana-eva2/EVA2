from django.urls import path

from . import views

urlpatterns = [

    # ==========================================
    # RUTAS DE REGISTRO DE BIOMETRÍA
    # ==========================================

    path(
        "",
        views.registrar_biometria,
        name="registrar_biometria"
    ),

    path(
        "registro/",
        views.registrar_biometria,
        name="registrar_biometria_alias"
    ),

    path(
        "guardar/",
        views.guardar_biometria,
        name="guardar_biometria"
    ),

    # ==========================================
    # RUTAS DE AUTENTICACIÓN Y PROCESAMIENTO
    # ==========================================

    path(
        "login/",
        views.login_biometrico,
        name="login_biometrico"
    ),

    path(
        "comparar/",
        views.comparar_rostro,
        name="comparar_rostro"
    ),

    path(
        "validar/",
        views.validar_rostro,
        name="validar_rostro"
    ),

    path(
        "detectar-vida/",
        views.detectar_vida,
        name="detectar_vida"
    ),

]