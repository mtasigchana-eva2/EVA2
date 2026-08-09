from django.urls import path
from . import views

urlpatterns = [
    path("", views.lista_solicitudes, name="lista_solicitudes"),
    path("nuevo/", views.nueva_solicitud, name="nueva_solicitud"),
    path("aprobar/<int:id>/", views.aprobar_solicitud, name="aprobar_solicitud"),
    path("rechazar/<int:id>/", views.rechazar_solicitud, name="rechazar_solicitud"),
    path("detalle/<int:id>/", views.detalle_solicitud, name="detalle_solicitud"),
    path("pdf/<int:id>/", views.exportar_pdf_solicitud, name="exportar_pdf_solicitud"),
]