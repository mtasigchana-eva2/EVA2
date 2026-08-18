import unicodedata
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from django.db.models import Q

# ReportLab para la generación del PDF estructurado en tabla
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from notificaciones.utils import enviar_notificacion_y_correo
from usuarios.permisos import (
    puede_editar_solicitudes,
    puede_eliminar_solicitudes,
    puede_aprobar_solicitudes,
)
from .models import SolicitudHerramienta
from .forms import SolicitudHerramientaForm


def normalizar_texto(val):
    """
    Convierte cualquier objeto o texto a una cadena limpia sin tildes ni caracteres
    especiales para evitar errores de codificación en el PDF.
    """
    if val is None:
        return "-"
    
    if hasattr(val, 'get_full_name') and callable(val.get_full_name):
        val = val.get_full_name() or getattr(val, 'username', str(val))
    
    texto = str(val)
    texto_sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    
    reemplazos = {'º': '.', '°': '.', 'ª': '.'}
    for orig, reemp in reemplazos.items():
        texto_sin_tildes = texto_sin_tildes.replace(orig, reemp)
        
    return texto_sin_tildes


def lista_solicitudes_herramientas(request):
    solicitudes = SolicitudHerramienta.objects.all().order_by("-fecha_registro")
    return render(
        request,
        "solicitudes_herramientas/index.html",
        {"solicitudes": solicitudes},
    )


def nueva_solicitud_herramienta(request):
    if request.method == "POST":
        formulario = SolicitudHerramientaForm(request.POST, request.FILES)

        if formulario.is_valid():
            solicitud = formulario.save(commit=False)
            
            # Estado Pendiente asignado por defecto
            if not request.user.is_superuser and (not hasattr(request.user, 'perfil') or request.user.perfil.rol == 'Estudiante'):
                solicitud.estado = "Pendiente"
            elif not solicitud.estado:
                solicitud.estado = "Pendiente"
                
            solicitud.save()

            destinatarios = []
            
            if solicitud.profesor:
                profesor_user = User.objects.filter(
                    Q(username__iexact=str(solicitud.profesor)) |
                    Q(first_name__icontains=str(solicitud.profesor))
                ).first()
                if profesor_user:
                    destinatarios.append(profesor_user)

            if not destinatarios:
                destinatarios = list(User.objects.filter(
                    Q(perfil__rol__iexact='Docente') |
                    Q(perfil__rol__iexact='Administrador Talleres') |
                    Q(perfil__rol__iexact='Coordinador Talleres') |
                    Q(perfil__rol__iexact='Coordinador Carrera') |
                    Q(perfil__rol__iexact='Superadministrador') |
                    Q(is_superuser=True)
                ).distinct())

            for destinatario in destinatarios:
                enviar_notificacion_y_correo(
                    usuario=destinatario,
                    titulo="Nueva Solicitud de Herramienta 🛠️",
                    mensaje=f"El estudiante {solicitud.estudiante} ha solicitado {solicitud.cantidad}x {solicitud.herramienta}.",
                    url_destino="/solicitudes-herramientas/"
                )

            messages.success(request, "Solicitud registrada correctamente.")
            return redirect("lista_solicitudes_herramientas")
    else:
        formulario = SolicitudHerramientaForm()

    return render(
        request,
        "solicitudes_herramientas/nuevo.html",
        {"formulario": formulario},
    )


def editar_solicitud_herramienta(request, id):
    if not puede_editar_solicitudes(request.user):
        return HttpResponseForbidden("Acceso denegado: Tu rol no tiene permisos para editar solicitudes.")

    solicitud = get_object_or_404(SolicitudHerramienta, id=id)

    if request.method == "POST":
        formulario = SolicitudHerramientaForm(request.POST, request.FILES, instance=solicitud)

        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Solicitud actualizada correctamente.")
            return redirect("lista_solicitudes_herramientas")
    else:
        formulario = SolicitudHerramientaForm(instance=solicitud)

    return render(
        request,
        "solicitudes_herramientas/nuevo.html",
        {"formulario": formulario},
    )


@require_POST
def eliminar_solicitud_herramienta(request, id):
    if not puede_eliminar_solicitudes(request.user):
        return HttpResponseForbidden("Acceso denegado: Tu rol no tiene permisos para eliminar solicitudes.")

    solicitud = get_object_or_404(SolicitudHerramienta, id=id)
    solicitud.delete()

    messages.success(request, "Solicitud eliminada correctamente.")
    return redirect("lista_solicitudes_herramientas")


@require_POST
def aprobar_solicitud_herramienta(request, id):
    if not puede_aprobar_solicitudes(request.user):
        return HttpResponseForbidden("Acceso denegado: Tu rol no tiene permisos para aprobar solicitudes.")

    solicitud = get_object_or_404(SolicitudHerramienta, id=id)
    solicitud.estado = "Aprobada"
    solicitud.save()

    herramienta = solicitud.herramienta
    herramienta.estado = "Prestada"
    herramienta.save()

    estudiante_user = User.objects.filter(
        Q(username__iexact=str(solicitud.estudiante)) |
        Q(perfil__rol__iexact='Estudiante', first_name__icontains=str(solicitud.estudiante))
    ).first()
    if estudiante_user:
        enviar_notificacion_y_correo(
            usuario=estudiante_user,
            titulo="Solicitud de Herramienta Aprobada 🛠️",
            mensaje=f"Tu solicitud para {solicitud.herramienta} ha sido APROBADA.",
            url_destino="/solicitudes-herramientas/"
        )

    messages.success(request, "Solicitud aprobada correctamente.")
    return redirect("lista_solicitudes_herramientas")


@require_POST
def rechazar_solicitud_herramienta(request, id):
    if not puede_aprobar_solicitudes(request.user):
        return HttpResponseForbidden("Acceso denegado: Tu rol no tiene permisos para rechazar solicitudes.")

    solicitud = get_object_or_404(SolicitudHerramienta, id=id)
    solicitud.estado = "Rechazada"
    solicitud.save()

    estudiante_user = User.objects.filter(
        Q(username__iexact=str(solicitud.estudiante)) |
        Q(perfil__rol__iexact='Estudiante', first_name__icontains=str(solicitud.estudiante))
    ).first()
    if estudiante_user:
        enviar_notificacion_y_correo(
            usuario=estudiante_user,
            titulo="Solicitud de Herramienta Rechazada 🛠️",
            mensaje=f"Tu solicitud para {solicitud.herramienta} ha sido RECHAZADA.",
            url_destino="/solicitudes-herramientas/"
        )

    messages.success(request, "Solicitud rechazada.")
    return redirect("lista_solicitudes_herramientas")


@require_POST
def devolver_herramienta(request, id):
    if not puede_aprobar_solicitudes(request.user):
        return HttpResponseForbidden("Acceso denegado: Tu rol no tiene permisos para procesar devoluciones.")

    solicitud = get_object_or_404(SolicitudHerramienta, id=id)

    herramienta = solicitud.herramienta
    herramienta.estado = "Disponible"
    herramienta.save()

    solicitud.estado = "Devuelta"
    solicitud.save()

    messages.success(request, "Herramienta devuelta correctamente.")
    return redirect("lista_solicitudes_herramientas")


def exportar_pdf_solicitud_herramienta(request, id):
    solicitud = get_object_or_404(SolicitudHerramienta, id=id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Solicitud_Herramienta_{solicitud.id}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Estilos de texto
    estilo_titulo_inst = ParagraphStyle(
        "TituloInst",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        alignment=1,
        textColor=colors.HexColor("#003366")
    )
    
    estilo_subtitulo_inst = ParagraphStyle(
        "SubTituloInst",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        alignment=1,
        textColor=colors.HexColor("#333333")
    )

    estilo_titulo_doc = ParagraphStyle(
        "TituloDoc",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        alignment=1,
        textColor=colors.HexColor("#003366"),
        spaceAfter=15
    )

    estilo_celda = ParagraphStyle(
        "Celda",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11
    )

    estilo_celda_bold = ParagraphStyle(
        "CeldaBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11
    )

    elementos = []

    # Encabezado Institucional
    elementos.append(Paragraph("INSTITUTO SUPERIOR TECNOLOGICO TECNOECUATORIANO", estilo_titulo_inst))
    elementos.append(Paragraph("SISTEMA INSTITUCIONAL SEMGA", estilo_subtitulo_inst))
    elementos.append(Spacer(1, 10))
    elementos.append(Paragraph("SOLICITUD DE HERRAMIENTA", estilo_titulo_doc))

    # Formateo de fecha de registro si existe
    fecha_reg = solicitud.fecha_registro.strftime("%d/%m/%Y") if getattr(solicitud, 'fecha_registro', None) else "-"

    # Matriz con los datos de la herramienta solicitada
    tabla_data = [
        [
            Paragraph("<b>N. Solicitud</b>", estilo_celda_bold),
            Paragraph(normalizar_texto(solicitud.id), estilo_celda),
            Paragraph("<b>Estado</b>", estilo_celda_bold),
            Paragraph(normalizar_texto(solicitud.estado), estilo_celda)
        ],
        [
            Paragraph("<b>Estudiante</b>", estilo_celda_bold),
            Paragraph(normalizar_texto(solicitud.estudiante), estilo_celda),
            Paragraph("<b>Carrera</b>", estilo_celda_bold),
            Paragraph(normalizar_texto(getattr(solicitud, 'carrera', 'N/A')), estilo_celda)
        ],
        [
            Paragraph("<b>Herramienta</b>", estilo_celda_bold),
            Paragraph(normalizar_texto(solicitud.herramienta), estilo_celda),
            Paragraph("<b>Cantidad</b>", estilo_celda_bold),
            Paragraph(normalizar_texto(solicitud.cantidad), estilo_celda)
        ],
        [
            Paragraph("<b>Docente / Profesor</b>", estilo_celda_bold),
            Paragraph(normalizar_texto(getattr(solicitud, 'profesor', 'N/A')), estilo_celda),
            Paragraph("<b>Fecha Registro</b>", estilo_celda_bold),
            Paragraph(fecha_reg, estilo_celda)
        ],
    ]

    t_principal = Table(tabla_data, colWidths=[110, 160, 110, 160])
    t_principal.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F2F2F2")),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor("#F2F2F2")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(t_principal)
    elementos.append(Spacer(1, 20))

    # Pie de página
    estilo_pie = ParagraphStyle(
        "Pie",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        alignment=1,
        textColor=colors.gray
    )
    elementos.append(Paragraph("Documento generado automaticamente por el Sistema Institucional SEMGA.", estilo_pie))

    doc.build(elementos)
    return response