from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseForbidden
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.auth.models import User
from django.db.models import Q

from notificaciones.utils import enviar_notificacion_y_correo
from usuarios.permisos import (
    puede_editar_solicitudes,
    puede_eliminar_solicitudes,
    puede_aprobar_solicitudes,
)
from .models import SolicitudHerramienta
from .forms import SolicitudHerramientaForm


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

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "TECNE ECUADOR")
    y -= 30

    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(50, y, "SOLICITUD DE HERRAMIENTA")
    y -= 40

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"ID Solicitud: {solicitud.id}")
    y -= 20
    pdf.drawString(50, y, f"Estudiante: {solicitud.estudiante}")
    y -= 20
    pdf.drawString(50, y, f"Carrera: {solicitud.carrera}")
    y -= 20
    pdf.drawString(50, y, f"Herramienta: {solicitud.herramienta}")
    y -= 20
    pdf.drawString(50, y, f"Cantidad: {solicitud.cantidad}")
    y -= 20
    pdf.drawString(50, y, f"Profesor: {solicitud.profesor}")
    y -= 20
    pdf.drawString(50, y, f"Estado: {solicitud.estado}")

    pdf.showPage()
    pdf.save()

    return response