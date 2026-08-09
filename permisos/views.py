from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.auth.models import User
from django.db.models import Q

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

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "TECNE ECUADOR")
    y -= 30

    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(50, y, "SOLICITUD DE PERMISO")
    y -= 40

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"ID Solicitud: {permiso.id}")
    y -= 20
    pdf.drawString(50, y, f"Estudiante: {permiso.estudiante}")
    y -= 20
    pdf.drawString(50, y, f"Carrera: {permiso.carrera}")
    y -= 20
    pdf.drawString(50, y, f"Docente: {permiso.docente}")
    y -= 20
    pdf.drawString(50, y, f"Desde: {permiso.fecha_inicio}")
    y -= 20
    pdf.drawString(50, y, f"Hasta: {permiso.fecha_fin}")
    y -= 20
    pdf.drawString(50, y, f"Estado: {permiso.estado}")

    pdf.showPage()
    pdf.save()

    return response