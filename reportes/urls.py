from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.index,
        name="lista_reportes"
    ),
    path(
        "inventario/",
        views.reporte_inventario,
        name="reporte_inventario"
    ),
    path(
        "solicitudes/",
        views.reporte_solicitudes,
        name="reporte_solicitudes"
    ),

    # ==========================
    # EXPORTAR PDF INDIVIDUALES
    # ==========================
    path(
        "solicitudes/pdf/<int:id>/",
        views.exportar_pdf_solicitud,
        name="exportar_pdf_solicitud"
    ),
    path(
        "herramientas/pdf/<int:id>/",
        views.exportar_pdf_herramienta,
        name="exportar_pdf_herramienta"
    ),
    path(
        "equipos/pdf/<int:id>/",
        views.exportar_pdf_equipo,
        name="exportar_pdf_equipo"
    ),
    path(
        "permisos/pdf/<int:id>/",
        views.exportar_pdf_permiso,
        name="exportar_pdf_permiso"
    ),

    # ==========================
    # EXPORTAR REPORTES GENERALES
    # ==========================
    path(
        "inventario/pdf/",
        views.exportar_inventario_pdf,
        name="exportar_inventario_pdf"
    ),
    path(
        "solicitudes/pdf/",
        views.exportar_solicitudes_pdf,
        name="exportar_solicitudes_pdf"
    ),
]