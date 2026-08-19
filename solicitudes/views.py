import unicodedata
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q

# ReportLab para la generación del PDF estructurado en tabla
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from notificaciones.utils import enviar_notificacion_y_correo
from .models import Solicitud
from .forms import SolicitudForm
from usuarios.permisos import puede_aprobar_solicitudes, puede_editar_solicitudes


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


def lista_solicitudes(request):
    solicitudes = Solicitud.objects.all().order_by("-id")
    return render(
        request,
        "solicitudes/index.html",
        {"solicitudes": solicitudes}
    )


def nueva_solicitud(request):
    if request.method == "POST":
        formulario = SolicitudForm(request.POST, request.FILES)
        if formulario.is_valid():
            solicitud = formulario.save(commit=False)
            solicitud.estudiante = request.user
            solicitud.save()

            destinatarios = []

            if hasattr(solicitud, 'docente') and solicitud.docente:
                user_doc = User.objects.filter(
                    Q(username__iexact=str(solicitud.docente)) |
                    Q(first_name__icontains=str(solicitud.docente))
                ).first()
                if user_doc:
                    destinatarios.append(user_doc)

            if not destinatarios:
                destinatarios = list(User.objects.filter(
                    Q(perfil__rol__iexact='Docente') |
                    Q(perfil__rol__iexact='Administrador Talleres') |
                    Q(perfil__rol__iexact='Coordinador Talleres') |
                    Q(perfil__rol__iexact='Coordinador Carrera') |
                    Q(perfil__rol__iexact='Superadministrador') |
                    Q(is_superuser=True)
                ).distinct())

            lab_nombre = getattr(solicitud, 'laboratorio', 'N/A')

            for usuario_destino in destinatarios:
                enviar_notificacion_y_correo(
                    usuario=usuario_destino,
                    titulo="Nueva Solicitud de Laboratorio 🔬",
                    mensaje=f"El estudiante {request.user.get_full_name() or request.user.username} ha solicitado el laboratorio {lab_nombre}.",
                    url_destino="/solicitudes/"
                )

            messages.success(request, "Solicitud registrada correctamente.")
            return redirect("lista_solicitudes")
    else:
        formulario = SolicitudForm()

    return render(
        request,
        "solicitudes/nuevo.html",
        {"formulario": formulario}
    )


def editar_solicitud(request, id):
    if not puede_editar_solicitudes(request.user):
        return HttpResponseForbidden("Acceso denegado: Tu rol no tiene permisos para editar solicitudes.")

    solicitud = get_object_or_404(Solicitud, id=id)

    if request.method == "POST":
        formulario = SolicitudForm(request.POST, request.FILES, instance=solicitud)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Solicitud actualizada correctamente.")
            return redirect("lista_solicitudes")
    else:
        formulario = SolicitudForm(instance=solicitud)

    return render(
        request,
        "solicitudes/nuevo.html",
        {"formulario": formulario, "solicitud": solicitud}
    )


def aprobar_solicitud(request, id):
    if not puede_aprobar_solicitudes(request.user):
        return HttpResponseForbidden("Acceso denegado: Tu rol no tiene permisos para aprobar solicitudes.")

    solicitud = get_object_or_404(Solicitud, id=id)
    solicitud.estado = "Aprobada"
    solicitud.aprobado_por = request.user
    solicitud.fecha_respuesta = timezone.now()
    solicitud.save()

    lab_nombre = getattr(solicitud, 'laboratorio', 'N/A')

    if solicitud.estudiante:
        enviar_notificacion_y_correo(
            usuario=solicitud.estudiante,
            titulo="Solicitud de Laboratorio Aprobada ✅",
            mensaje=f"Tu solicitud para el laboratorio {lab_nombre} ha sido APROBADA.",
            url_destino="/solicitudes/"
        )

    messages.success(request, "Solicitud aprobada correctamente.")
    return redirect("lista_solicitudes")


def rechazar_solicitud(request, id):
    if not puede_aprobar_solicitudes(request.user):
        return HttpResponseForbidden("Acceso denegado: Tu rol no tiene permisos para rechazar solicitudes.")

    solicitud = get_object_or_404(Solicitud, id=id)

    if request.method == "POST":
        solicitud.estado = "Rechazada"
        solicitud.observacion = request.POST.get("observacion")
        solicitud.aprobado_por = request.user
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save()

        lab_nombre = getattr(solicitud, 'laboratorio', 'N/A')

        if solicitud.estudiante:
            enviar_notificacion_y_correo(
                usuario=solicitud.estudiante,
                titulo="Solicitud de Laboratorio Rechazada ❌",
                mensaje=f"Tu solicitud para el laboratorio {lab_nombre} ha sido RECHAZADA. Observación: {solicitud.observacion or 'Sin observaciones'}.",
                url_destino="/solicitudes/"
            )

        messages.success(request, "Solicitud rechazada correctamente.")
        return redirect("lista_solicitudes")

    return render(
        request,
        "solicitudes/rechazar.html",
        {"solicitud": solicitud}
    )


def detalle_solicitud(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)
    return render(
        request,
        "solicitudes/detalle.html",
        {"solicitud": solicitud}
    )


def exportar_pdf_solicitud(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Solicitud_{solicitud.id}.pdf"'

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
    elementos.append(Paragraph("SISTEMA INSTITUCIONAL EVA2", estilo_subtitulo_inst))
    elementos.append(Spacer(1, 10))
    elementos.append(Paragraph("SOLICITUD DE LABORATORIO", estilo_titulo_doc))

    # Formateo de fechas y horas
    fecha_sol = getattr(solicitud, 'fecha', None)
    f_fecha = fecha_sol.strftime("%d/%m/%Y") if hasattr(fecha_sol, 'strftime') else str(fecha_sol or '-')
    
    h_inicio = getattr(solicitud, 'hora_inicio', '') or ''
    h_fin = getattr(solicitud, 'hora_fin', '') or ''
    horario_txt = f"{h_inicio} - {h_fin}" if h_inicio else "-"

    # Matriz de la tabla principal
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
            Paragraph("<b>Laboratorio</b>", estilo_celda_bold),
            Paragraph(normalizar_texto(getattr(solicitud, 'laboratorio', 'N/A')), estilo_celda),
            Paragraph("<b>Sede</b>", estilo_celda_bold),
            Paragraph(normalizar_texto(getattr(solicitud, 'sede', 'N/A')), estilo_celda)
        ],
        [
            Paragraph("<b>Docente</b>", estilo_celda_bold),
            Paragraph(normalizar_texto(getattr(solicitud, 'docente', 'N/A')), estilo_celda),
            Paragraph("<b>Fecha Reserva</b>", estilo_celda_bold),
            Paragraph(f_fecha, estilo_celda)
        ],
        [
            Paragraph("<b>Horario</b>", estilo_celda_bold),
            Paragraph(normalizar_texto(horario_txt), estilo_celda),
            Paragraph("", estilo_celda),
            Paragraph("", estilo_celda)
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
    elementos.append(Spacer(1, 15))

    # Sección Motivo u Observaciones
    motivo_texto = getattr(solicitud, 'motivo', '') or 'Sin motivo especificado.'
    obs_texto = getattr(solicitud, 'observacion', '') or 'Ninguna'
    
    tabla_motivo_data = [
        [Paragraph("<b>MOTIVO DE LA SOLICITUD</b>", estilo_celda_bold)],
        [Paragraph(normalizar_texto(motivo_texto), estilo_celda)],
        [Paragraph("<b>OBSERVACIONES / RESPUESTA</b>", estilo_celda_bold)],
        [Paragraph(normalizar_texto(obs_texto), estilo_celda)]
    ]
    
    t_motivo = Table(tabla_motivo_data, colWidths=[540])
    t_motivo.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E6EEF8")),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor("#E6EEF8")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(t_motivo)
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
    elementos.append(Paragraph("Documento generado automaticamente por el Sistema Institucional EVA2.", estilo_pie))

    doc.build(elementos)
    return response