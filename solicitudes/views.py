from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.auth.models import User
from django.db.models import Q

from notificaciones.utils import enviar_notificacion_y_correo
from .models import Solicitud
from .forms import SolicitudForm
from usuarios.permisos import puede_aprobar_solicitudes


def lista_solicitudes(request):
    solicitudes = Solicitud.objects.all()
    return render(
        request,
        "solicitudes/index.html",
        {"solicitudes": solicitudes}
    )


def nueva_solicitud(request):
    if request.method == "POST":
        # Se agrega request.FILES para procesar el campo documento/adjunto
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

            return redirect("lista_solicitudes")
    else:
        formulario = SolicitudForm()

    return render(
        request,
        "solicitudes/nuevo.html",
        {"formulario": formulario}
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

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "TECNE ECUADOR")
    y -= 30

    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(50, y, "SOLICITUD DE LABORATORIO")
    y -= 40

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"ID: {solicitud.id}")
    y -= 20

    pdf.drawString(
        50,
        y,
        f"Estudiante: {solicitud.estudiante.get_full_name() or solicitud.estudiante.username}"
    )
    y -= 20
    pdf.drawString(50, y, f"Carrera: {getattr(solicitud, 'carrera', 'N/A')}")
    y -= 20
    pdf.drawString(50, y, f"Sede: {getattr(solicitud, 'sede', 'N/A')}")
    y -= 20
    pdf.drawString(50, y, f"Laboratorio: {getattr(solicitud, 'laboratorio', 'N/A')}")
    y -= 20
    pdf.drawString(50, y, f"Docente: {getattr(solicitud, 'docente', 'N/A')}")
    y -= 20
    pdf.drawString(50, y, f"Fecha: {getattr(solicitud, 'fecha', 'N/A')}")
    y -= 20

    pdf.drawString(
        50,
        y,
        f"Horario: {getattr(solicitud, 'hora_inicio', '')} - {getattr(solicitud, 'hora_fin', '')}"
    )
    y -= 30

    pdf.drawString(50, y, "Motivo:")
    y -= 20

    texto = pdf.beginText(50, y)
    texto.setFont("Helvetica", 12)

    motivo = getattr(solicitud, 'motivo', '') or ''
    for linea in motivo.split("\n"):
        texto.textLine(linea)

    pdf.drawText(texto)
    y = texto.getY() - 20

    pdf.drawString(50, y, f"Estado: {solicitud.estado}")
    y -= 20
    pdf.drawString(50, y, f"Observación: {getattr(solicitud, 'observacion', 'Ninguna') or 'Ninguna'}")

    pdf.showPage()
    pdf.save()

    return response