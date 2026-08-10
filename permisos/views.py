from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q

# ReportLab para generar el PDF en tabla estructurada
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from notificaciones.utils import enviar_notificacion_y_correo
from .models import Permiso
from .forms import PermisoForm


def lista_permisos(request):
    permisos = Permiso.objects.all().order_by("-fecha_solicitud")
    return render(
        request,
        "permisos/index.html",
        {"permisos": permisos}
    )


def nuevo_permiso(request):
    if request.method == "POST":
        formulario = PermisoForm(request.POST, request.FILES)
        if formulario.is_valid():
            permiso = formulario.save(commit=False)
            
            # Asignación automática del estado a Pendiente
            if not request.user.is_superuser and (not hasattr(request.user, 'perfil') or request.user.perfil.rol == 'Estudiante'):
                permiso.estado = "Pendiente"
            elif not permiso.estado:
                permiso.estado = "Pendiente"
                
            permiso.save()

            destinatarios = []
            
            if hasattr(permiso, 'docente') and permiso.docente:
                if isinstance(permiso.docente, User):
                    destinatarios.append(permiso.docente)
                else:
                    user_doc = User.objects.filter(
                        Q(username__iexact=str(permiso.docente)) |
                        Q(first_name__icontains=str(permiso.docente))
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

            for destinatario in destinatarios:
                enviar_notificacion_y_correo(
                    usuario=destinatario,
                    titulo="Nueva Solicitud de Permiso 📜",
                    mensaje=f"El estudiante {permiso.estudiante} ha registrado una nueva solicitud de permiso.",
                    url_destino="/permisos/"
                )

            messages.success(request, "Solicitud registrada correctamente.")
            return redirect("lista_permisos")
    else:
        formulario = PermisoForm()

    return render(
        request,
        "permisos/nuevo.html",
        {"formulario": formulario}
    )


def editar_permiso(request, id):
    permiso = get_object_or_404(Permiso, id=id)

    if request.method == "POST":
        formulario = PermisoForm(request.POST, request.FILES, instance=permiso)
        if formulario.is_valid():
            permiso_previo_estado = permiso.estado
            permiso_actualizado = formulario.save()

            if permiso_previo_estado != permiso_actualizado.estado:
                estudiante_user = User.objects.filter(
                    Q(username__iexact=str(permiso_actualizado.estudiante)) |
                    Q(perfil__rol__iexact='Estudiante', first_name__icontains=str(permiso_actualizado.estudiante))
                ).first()
                if estudiante_user:
                    enviar_notificacion_y_correo(
                        usuario=estudiante_user,
                        titulo=f"Solicitud de Permiso: {permiso_actualizado.estado} 📜",
                        mensaje=f"Tu solicitud de permiso ha cambiado al estado: {permiso_actualizado.estado}.",
                        url_destino="/permisos/"
                    )

            messages.success(request, "Solicitud actualizada correctamente.")
            return redirect("lista_permisos")
    else:
        formulario = PermisoForm(instance=permiso)

    return render(
        request,
        "permisos/nuevo.html",
        {"formulario": formulario}
    )


def eliminar_permiso(request, id):
    permiso = get_object_or_404(Permiso, id=id)
    permiso.delete()
    messages.success(request, "Solicitud eliminada correctamente.")
    return redirect("lista_permisos")


def exportar_pdf_permiso(request, id):
    permiso = get_object_or_404(Permiso, id=id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Solicitud_Permiso_{permiso.id}.pdf"'

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
        alignment=1, # Centrado
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
    elementos.append(Paragraph("INSTITUTO SUPERIOR TECNOLÓGICO TECNOECUATORIANO", estilo_titulo_inst))
    elementos.append(Paragraph("SISTEMA INSTITUCIONAL EVA2", estilo_subtitulo_inst))
    elementos.append(Spacer(1, 10))
    elementos.append(Paragraph("SOLICITUD DE PERMISO", estilo_titulo_doc))

    # Formateo de fechas
    f_inicio = permiso.fecha_inicio.strftime("%d/%m/%Y") if getattr(permiso, 'fecha_inicio', None) else "-"
    f_fin = permiso.fecha_fin.strftime("%d/%m/%Y") if getattr(permiso, 'fecha_fin', None) else "-"

    # Matriz de la tabla principal de datos
    tabla_data = [
        [
            Paragraph("<b>N.º de solicitud</b>", estilo_celda_bold),
            Paragraph(str(permiso.id), estilo_celda),
            Paragraph("<b>Estado</b>", estilo_celda_bold),
            Paragraph(str(permiso.estado), estilo_celda)
        ],
        [
            Paragraph("<b>Estudiante</b>", estilo_celda_bold),
            Paragraph(str(permiso.estudiante), estilo_celda),
            Paragraph("<b>Carrera</b>", estilo_celda_bold),
            Paragraph(str(getattr(permiso, 'carrera', 'N/A')), estilo_celda)
        ],
        [
            Paragraph("<b>Docente</b>", estilo_celda_bold),
            Paragraph(str(getattr(permiso, 'docente', 'N/A')), estilo_celda),
            Paragraph("<b>Fecha Inicio</b>", estilo_celda_bold),
            Paragraph(f_inicio, estilo_celda)
        ],
        [
            Paragraph("<b>Fecha Fin</b>", estilo_celda_bold),
            Paragraph(f_fin, estilo_celda),
            Paragraph("", estilo_celda),
            Paragraph("", estilo_celda)
        ],
    ]

    # Diseño visual de la cuadrícula
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

    # Sección Motivo / Observaciones
    motivo_texto = getattr(permiso, 'motivo', None) or getattr(permiso, 'descripcion', 'Sin motivo especificado.')
    
    tabla_motivo_data = [
        [Paragraph("<b>MOTIVO DE LA SOLICITUD</b>", estilo_celda_bold)],
        [Paragraph(str(motivo_texto), estilo_celda)]
    ]
    
    t_motivo = Table(tabla_motivo_data, colWidths=[540])
    t_motivo.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E6EEF8")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(t_motivo)
    elementos.append(Spacer(1, 20))

    # Pie de página informativo
    estilo_pie = ParagraphStyle(
        "Pie",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        alignment=1,
        textColor=colors.gray
    )
    elementos.append(Paragraph("Documento generado automáticamente por el Sistema Institucional EVA2.", estilo_pie))

    doc.build(elementos)
    return response