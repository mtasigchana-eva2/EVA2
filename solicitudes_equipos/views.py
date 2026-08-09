from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.auth.models import User
from django.db.models import Q

from notificaciones.utils import enviar_notificacion_y_correo
from usuarios.permisos import puede_editar_solicitudes, puede_eliminar_solicitudes
from .models import SolicitudEquipo
from .forms import SolicitudEquipoForm


def lista_solicitudes_equipos(request):
    solicitudes = SolicitudEquipo.objects.all().order_by("-fecha_registro")
    return render(
        request,
        "solicitudes_equipos/index.html",
        {"solicitudes": solicitudes}
    )


def nueva_solicitud_equipo(request):
    if request.method == "POST":
        formulario = SolicitudEquipoForm(request.POST, request.FILES)

        if formulario.is_valid():
            solicitud = formulario.save(commit=False)
            
            # Estado Pendiente forzado por defecto
            if not request.user.is_superuser and (not hasattr(request.user, 'perfil') or request.user.perfil.rol == 'Estudiante'):
                solicitud.estado = "Pendiente"
            elif not solicitud.estado:
                solicitud.estado = "Pendiente"
                
            solicitud.save()

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
                    titulo="Nueva Solicitud de Equipo 💻",
                    mensaje=f"El estudiante {solicitud.estudiante} solicitó el equipo {solicitud.equipo}.",
                    url_destino="/solicitudes-equipos/"
                )

            messages.success(request, "Solicitud registrada correctamente.")
            return redirect("lista_solicitudes_equipos")
    else:
        formulario = SolicitudEquipoForm()

    return render(
        request,
        "solicitudes_equipos/nuevo.html",
        {"formulario": formulario}
    )


def editar_solicitud_equipo(request, id):
    if not puede_editar_solicitudes(request.user):
        return HttpResponseForbidden("Acceso denegado: Tu rol no tiene permisos para editar solicitudes de equipos.")

    solicitud = get_object_or_404(SolicitudEquipo, id=id)

    if request.method == "POST":
        formulario = SolicitudEquipoForm(request.POST, request.FILES, instance=solicitud)

        if formulario.is_valid():
            estado_anterior = solicitud.estado
            solicitud_actualizada = formulario.save()

            if estado_anterior != solicitud_actualizada.estado:
                estudiante_user = User.objects.filter(
                    Q(username__iexact=str(solicitud_actualizada.estudiante)) |
                    Q(perfil__rol__iexact='Estudiante', first_name__icontains=str(solicitud_actualizada.estudiante))
                ).first()
                if estudiante_user:
                    enviar_notificacion_y_correo(
                        usuario=estudiante_user,
                        titulo=f"Solicitud de Equipo: {solicitud_actualizada.estado} 💻",
                        mensaje=f"Tu solicitud para el equipo {solicitud_actualizada.equipo} ha sido {solicitud_actualizada.estado}.",
                        url_destino="/solicitudes-equipos/"
                    )

            messages.success(request, "Solicitud actualizada correctamente.")
            return redirect("lista_solicitudes_equipos")
    else:
        formulario = SolicitudEquipoForm(instance=solicitud)

    return render(
        request,
        "solicitudes_equipos/nuevo.html",
        {"formulario": formulario, "solicitud": solicitud}
    )


def eliminar_solicitud_equipo(request, id):
    if not puede_eliminar_solicitudes(request.user):
        return HttpResponseForbidden("Acceso denegado: Tu rol no tiene permisos para eliminar solicitudes de equipos.")

    solicitud = get_object_or_404(SolicitudEquipo, id=id)
    solicitud.delete()

    messages.success(request, "Solicitud eliminada correctamente.")
    return redirect("lista_solicitudes_equipos")


def exportar_pdf_solicitud_equipo(request, id):
    solicitud = get_object_or_404(SolicitudEquipo, id=id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Solicitud_Equipo_{solicitud.id}.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "TECNE ECUADOR")
    y -= 30

    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(50, y, "SOLICITUD DE EQUIPO")
    y -= 40

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"ID Solicitud: {solicitud.id}")
    y -= 20
    pdf.drawString(50, y, f"Estudiante: {solicitud.estudiante}")
    y -= 20
    pdf.drawString(50, y, f"Equipo: {solicitud.equipo}")
    y -= 20
    pdf.drawString(50, y, f"Cantidad: {solicitud.cantidad}")
    y -= 20
    pdf.drawString(50, y, f"Estado: {solicitud.estado}")

    pdf.showPage()
    pdf.save()

    return response


def aprobar_solicitud_equipo(request, id):
    if not puede_editar_solicitudes(request.user):
        return HttpResponseForbidden("Acceso denegado.")

    solicitud = get_object_or_404(SolicitudEquipo, id=id)
    solicitud.estado = "Aprobada"
    solicitud.save()

    estudiante_user = User.objects.filter(
        Q(username__iexact=str(solicitud.estudiante)) |
        Q(perfil__rol__iexact='Estudiante', first_name__icontains=str(solicitud.estudiante))
    ).first()

    if estudiante_user:
        enviar_notificacion_y_correo(
            usuario=estudiante_user,
            titulo="Solicitud de Equipo: Aprobada 💻",
            mensaje=f"Tu solicitud para el equipo {solicitud.equipo} ha sido Aprobada.",
            url_destino="/solicitudes-equipos/"
        )

    messages.success(request, f"La solicitud #{solicitud.id} ha sido APROBADA exitosamente.")
    return redirect("lista_solicitudes_equipos")


def rechazar_solicitud_equipo(request, id):
    if not puede_editar_solicitudes(request.user):
        return HttpResponseForbidden("Acceso denegado.")

    solicitud = get_object_or_404(SolicitudEquipo, id=id)
    solicitud.estado = "Rechazada"
    solicitud.save()

    estudiante_user = User.objects.filter(
        Q(username__iexact=str(solicitud.estudiante)) |
        Q(perfil__rol__iexact='Estudiante', first_name__icontains=str(solicitud.estudiante))
    ).first()

    if estudiante_user:
        enviar_notificacion_y_correo(
            usuario=estudiante_user,
            titulo="Solicitud de Equipo: Rechazada 💻",
            mensaje=f"Tu solicitud para el equipo {solicitud.equipo} ha sido Rechazada.",
            url_destino="/solicitudes-equipos/"
        )

    messages.error(request, f"La solicitud #{solicitud.id} ha sido RECHAZADA.")
    return redirect("lista_solicitudes_equipos")