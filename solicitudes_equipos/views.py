import unicodedata

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages

from django.http import (
    HttpResponse,
    HttpResponseForbidden
)

from django.contrib.auth.models import User

from django.db import transaction

from django.db.models import Q

# ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from notificaciones.utils import (
    enviar_notificacion_y_correo
)

from usuarios.permisos import (
    puede_editar_solicitudes,
)

from .models import SolicitudEquipo

from .forms import SolicitudEquipoForm

from inventario.models import Inventario


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def normalizar_texto(val):
    """
    Convierte cualquier objeto o texto a una cadena limpia
    sin tildes ni caracteres especiales para evitar errores
    de codificación en el PDF.
    """

    if val is None:
        return "-"

    if hasattr(
        val,
        "get_full_name"
    ) and callable(
        val.get_full_name
    ):

        val = (
            val.get_full_name()
            or getattr(
                val,
                "username",
                str(val)
            )
        )

    texto = str(val)

    texto_sin_tildes = "".join(
        c
        for c in unicodedata.normalize(
            "NFD",
            texto
        )
        if unicodedata.category(c) != "Mn"
    )

    reemplazos = {
        "º": ".",
        "°": ".",
        "ª": ".",
    }

    for orig, reemp in reemplazos.items():

        texto_sin_tildes = (
            texto_sin_tildes.replace(
                orig,
                reemp
            )
        )

    return texto_sin_tildes


def usuario_es_estudiante(user):
    """
    Solamente el rol Estudiante recibe la restricción.

    Los demás roles conservan su comportamiento actual.
    """

    if user.is_superuser:
        return False

    perfil = getattr(
        user,
        "perfil",
        None
    )

    if not perfil:
        return False

    return perfil.rol == "Estudiante"


def estudiante_puede_ver_solicitud(
    user,
    solicitud
):
    """
    Un estudiante solamente puede ver sus propias
    solicitudes.

    Los demás roles pueden ver todas.
    """

    if not usuario_es_estudiante(user):
        return True

    valores_permitidos = {
        user.username.strip().casefold()
    }

    nombre_completo = (
        user.get_full_name().strip()
    )

    if nombre_completo:

        valores_permitidos.add(
            nombre_completo.casefold()
        )

    estudiante_guardado = str(
        solicitud.estudiante
    ).strip().casefold()

    return (
        estudiante_guardado
        in valores_permitidos
    )


def obtener_solicitud_permitida(
    request,
    id
):

    solicitud = get_object_or_404(
        SolicitudEquipo,
        id=id
    )

    if not estudiante_puede_ver_solicitud(
        request.user,
        solicitud
    ):

        return None

    return solicitud


# ============================================================
# INVENTARIO
# ============================================================

@transaction.atomic
def descontar_inventario(
    solicitud
):
    """
    Descuenta las unidades del inventario cuando una
    solicitud es aprobada.

    Ejemplo:

    Total = 10
    Prestado = 0
    Solicitud = 1

    Resultado:

    Total = 10
    Prestado = 1
    Disponible = 9
    """

    if solicitud.inventario_descontado:
        return True

    equipo = (
        Inventario.objects
        .select_for_update()
        .get(
            id=solicitud.equipo_id
        )
    )

    disponible = (
        equipo.cantidad_disponible
    )

    if solicitud.cantidad > disponible:

        return False

    equipo.cantidad_prestada += (
        solicitud.cantidad
    )

    equipo.actualizar_estado()

    equipo.save(
        update_fields=[
            "cantidad_prestada",
            "estado",
        ]
    )

    solicitud.inventario_descontado = True

    solicitud.save(
        update_fields=[
            "inventario_descontado"
        ]
    )

    return True


@transaction.atomic
def devolver_inventario(
    solicitud
):
    """
    Devuelve al inventario las unidades que habían sido
    prestadas por esta solicitud.

    Ejemplo:

    Total = 10
    Prestado = 1
    Disponible = 9

    Al devolver:

    Total = 10
    Prestado = 0
    Disponible = 10
    """

    if not solicitud.inventario_descontado:
        return True

    equipo = (
        Inventario.objects
        .select_for_update()
        .get(
            id=solicitud.equipo_id
        )
    )

    equipo.cantidad_prestada = max(
        equipo.cantidad_prestada
        - solicitud.cantidad,
        0
    )

    equipo.actualizar_estado()

    equipo.save(
        update_fields=[
            "cantidad_prestada",
            "estado",
        ]
    )

    solicitud.inventario_descontado = False

    solicitud.save(
        update_fields=[
            "inventario_descontado"
        ]
    )

    return True


# ============================================================
# LISTA
# ============================================================

def lista_solicitudes_equipos(
    request
):

    if usuario_es_estudiante(
        request.user
    ):

        valores_permitidos = Q(
            estudiante__iexact=(
                request.user.username
            )
        )

        nombre_completo = (
            request.user.get_full_name().strip()
        )

        if nombre_completo:

            valores_permitidos |= Q(
                estudiante__iexact=(
                    nombre_completo
                )
            )

        solicitudes = (
            SolicitudEquipo.objects
            .select_related("equipo")
            .filter(
                valores_permitidos
            )
            .order_by(
                "-fecha_registro"
            )
        )

    else:

        solicitudes = (
            SolicitudEquipo.objects
            .select_related("equipo")
            .all()
            .order_by(
                "-fecha_registro"
            )
        )

    return render(
        request,
        "solicitudes_equipos/index.html",
        {
            "solicitudes": solicitudes
        }
    )


# ============================================================
# NUEVA SOLICITUD
# ============================================================

def nueva_solicitud_equipo(
    request
):

    if request.method == "POST":

        formulario = SolicitudEquipoForm(
            request.POST,
            request.FILES
        )

        if formulario.is_valid():

            solicitud = formulario.save(
                commit=False
            )

            # El estado inicial es Pendiente.
            solicitud.estado = "Pendiente"

            # Todavía NO descontamos inventario.
            solicitud.inventario_descontado = False

            solicitud.save()

            # ------------------------------------------------
            # NOTIFICACIONES
            # ------------------------------------------------

            try:

                destinatarios = list(
                    User.objects.filter(
                        Q(
                            perfil__rol__iexact="Docente"
                        )
                        |
                        Q(
                            perfil__rol__iexact=(
                                "Administrador Talleres"
                            )
                        )
                        |
                        Q(
                            perfil__rol__iexact=(
                                "Coordinador Talleres"
                            )
                        )
                        |
                        Q(
                            perfil__rol__iexact=(
                                "Coordinador Carrera"
                            )
                        )
                        |
                        Q(
                            perfil__rol__iexact=(
                                "Superadministrador"
                            )
                        )
                        |
                        Q(
                            is_superuser=True
                        )
                    ).distinct()
                )

                for destinatario in destinatarios:

                    try:

                        enviar_notificacion_y_correo(
                            usuario=destinatario,
                            titulo=(
                                "Nueva Solicitud de Equipo 💻"
                            ),
                            mensaje=(
                                f"El estudiante "
                                f"{solicitud.estudiante} "
                                f"solicitó "
                                f"{solicitud.cantidad} "
                                f"unidad(es) del equipo "
                                f"{solicitud.equipo}."
                            ),
                            url_destino=(
                                "/solicitudes-equipos/"
                            ),
                        )

                    except Exception as error_notificacion:

                        print(
                            "ERROR AL ENVIAR "
                            "NOTIFICACIÓN DE "
                            "SOLICITUD DE EQUIPO: "
                            f"{error_notificacion}"
                        )

            except Exception as error_general:

                print(
                    "ERROR GENERAL EN "
                    "NOTIFICACIONES DE "
                    "SOLICITUD DE EQUIPO: "
                    f"{error_general}"
                )

            messages.success(
                request,
                "Solicitud registrada correctamente."
            )

            return redirect(
                "lista_solicitudes_equipos"
            )

    else:

        formulario = SolicitudEquipoForm()

    return render(
        request,
        "solicitudes_equipos/nuevo.html",
        {
            "formulario": formulario
        }
    )


# ============================================================
# EDITAR SOLICITUD
# ============================================================

@transaction.atomic
def editar_solicitud_equipo(
    request,
    id
):

    if not puede_editar_solicitudes(
        request.user
    ):

        return HttpResponseForbidden(
            "Acceso denegado: Tu rol no tiene "
            "permisos para editar solicitudes "
            "de equipos."
        )

    solicitud = get_object_or_404(
        SolicitudEquipo,
        id=id
    )

    estado_anterior = (
        solicitud.estado
    )

    cantidad_anterior = (
        solicitud.cantidad
    )

    equipo_anterior_id = (
        solicitud.equipo_id
    )

    if request.method == "POST":

        formulario = SolicitudEquipoForm(
            request.POST,
            request.FILES,
            instance=solicitud
        )

        if formulario.is_valid():

            solicitud_actualizada = (
                formulario.save(
                    commit=False
                )
            )

            estado_nuevo = (
                solicitud_actualizada.estado
            )

            # ------------------------------------------------
            # CASO 1:
            # LA SOLICITUD YA ESTABA APROBADA
            # ------------------------------------------------

            if estado_anterior == "Aprobada":

                # Si cambia el equipo o la cantidad,
                # primero devolvemos el inventario anterior.
                if (
                    cantidad_anterior
                    != solicitud_actualizada.cantidad
                    or
                    equipo_anterior_id
                    != solicitud_actualizada.equipo_id
                ):

                    devolver_inventario(
                        solicitud
                    )

                    solicitud_actualizada.inventario_descontado = False

                # Si sigue aprobada, volvemos a descontar
                # la nueva cantidad.
                if estado_nuevo == "Aprobada":

                    solicitud_actualizada.save()

                    resultado = (
                        descontar_inventario(
                            solicitud_actualizada
                        )
                    )

                    if not resultado:

                        messages.error(
                            request,
                            "No hay suficiente stock "
                            "disponible para actualizar "
                            "esta solicitud."
                        )

                        return render(
                            request,
                            "solicitudes_equipos/nuevo.html",
                            {
                                "formulario": formulario,
                                "solicitud": solicitud,
                            }
                        )

                elif estado_nuevo == "Devuelta":

                    solicitud_actualizada.save()

                    # Ya fue devuelto arriba.
                    solicitud_actualizada.inventario_descontado = False

                    solicitud_actualizada.save(
                        update_fields=[
                            "inventario_descontado"
                        ]
                    )

                else:

                    solicitud_actualizada.save()

            # ------------------------------------------------
            # CASO 2:
            # NO ESTABA APROBADA
            # ------------------------------------------------

            else:

                solicitud_actualizada.save()

                if estado_nuevo == "Aprobada":

                    resultado = (
                        descontar_inventario(
                            solicitud_actualizada
                        )
                    )

                    if not resultado:

                        solicitud_actualizada.estado = (
                            estado_anterior
                        )

                        solicitud_actualizada.save(
                            update_fields=[
                                "estado"
                            ]
                        )

                        messages.error(
                            request,
                            "No hay suficiente stock "
                            "disponible para aprobar "
                            "esta solicitud."
                        )

                        return render(
                            request,
                            "solicitudes_equipos/nuevo.html",
                            {
                                "formulario": formulario,
                                "solicitud": solicitud,
                            }
                        )

            # ------------------------------------------------
            # NOTIFICAR CAMBIO DE ESTADO
            # ------------------------------------------------

            if (
                estado_anterior
                != solicitud_actualizada.estado
            ):

                estudiante_user = User.objects.filter(
                    Q(
                        username__iexact=str(
                            solicitud_actualizada.estudiante
                        )
                    )
                    |
                    Q(
                        perfil__rol__iexact="Estudiante",
                        first_name__icontains=str(
                            solicitud_actualizada.estudiante
                        )
                    )
                ).first()

                if estudiante_user:

                    enviar_notificacion_y_correo(
                        usuario=estudiante_user,
                        titulo=(
                            "Solicitud de Equipo: "
                            f"{solicitud_actualizada.estado} 💻"
                        ),
                        mensaje=(
                            "Tu solicitud para el equipo "
                            f"{solicitud_actualizada.equipo} "
                            f"ha sido "
                            f"{solicitud_actualizada.estado}."
                        ),
                        url_destino=(
                            "/solicitudes-equipos/"
                        )
                    )

            messages.success(
                request,
                "Solicitud actualizada correctamente."
            )

            return redirect(
                "lista_solicitudes_equipos"
            )

    else:

        formulario = SolicitudEquipoForm(
            instance=solicitud
        )

    return render(
        request,
        "solicitudes_equipos/nuevo.html",
        {
            "formulario": formulario,
            "solicitud": solicitud,
        }
    )


# ============================================================
# ELIMINAR SOLICITUD
# ============================================================

@transaction.atomic
def eliminar_solicitud_equipo(
    request,
    id
):

    if not puede_editar_solicitudes(
        request.user
    ):

        return HttpResponseForbidden(
            "Acceso denegado: Tu rol no tiene "
            "permisos para eliminar solicitudes "
            "de equipos."
        )

    solicitud = get_object_or_404(
        SolicitudEquipo,
        id=id
    )

    # Si estaba prestado, primero devolvemos
    # las unidades al inventario.
    if solicitud.inventario_descontado:

        devolver_inventario(
            solicitud
        )

    solicitud.delete()

    messages.success(
        request,
        "Solicitud eliminada correctamente."
    )

    return redirect(
        "lista_solicitudes_equipos"
    )


# ============================================================
# PDF
# ============================================================

def exportar_pdf_solicitud_equipo(
    request,
    id
):

    solicitud = obtener_solicitud_permitida(
        request,
        id
    )

    if solicitud is None:

        return HttpResponseForbidden(
            "Acceso denegado: Un estudiante "
            "solamente puede descargar sus "
            "propias solicitudes."
        )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = (
        "attachment; "
        f'filename="Solicitud_Equipo_{solicitud.id}.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    estilo_titulo_inst = ParagraphStyle(
        "TituloInst",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        alignment=1,
        textColor=colors.HexColor(
            "#003366"
        ),
    )

    estilo_subtitulo_inst = ParagraphStyle(
        "SubTituloInst",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        alignment=1,
        textColor=colors.HexColor(
            "#333333"
        ),
    )

    estilo_titulo_doc = ParagraphStyle(
        "TituloDoc",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        alignment=1,
        textColor=colors.HexColor(
            "#003366"
        ),
        spaceAfter=15,
    )

    estilo_celda = ParagraphStyle(
        "Celda",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
    )

    estilo_celda_bold = ParagraphStyle(
        "CeldaBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
    )

    elementos = []

    elementos.append(
        Paragraph(
            "INSTITUTO SUPERIOR TECNOLOGICO TECNOECUATORIANO",
            estilo_titulo_inst,
        )
    )

    elementos.append(
        Paragraph(
            "SISTEMA INSTITUCIONAL SEMGA",
            estilo_subtitulo_inst,
        )
    )

    elementos.append(
        Spacer(
            1,
            10
        )
    )

    elementos.append(
        Paragraph(
            "SOLICITUD DE EQUIPO",
            estilo_titulo_doc,
        )
    )

    fecha_reg = (
        solicitud.fecha_registro.strftime(
            "%d/%m/%Y"
        )
        if getattr(
            solicitud,
            "fecha_registro",
            None
        )
        else "-"
    )

    tabla_data = [

        [
            Paragraph(
                "<b>N. Solicitud</b>",
                estilo_celda_bold
            ),
            Paragraph(
                normalizar_texto(
                    solicitud.id
                ),
                estilo_celda
            ),
            Paragraph(
                "<b>Estado</b>",
                estilo_celda_bold
            ),
            Paragraph(
                normalizar_texto(
                    solicitud.estado
                ),
                estilo_celda
            ),
        ],

        [
            Paragraph(
                "<b>Estudiante</b>",
                estilo_celda_bold
            ),
            Paragraph(
                normalizar_texto(
                    solicitud.estudiante
                ),
                estilo_celda
            ),
            Paragraph(
                "<b>Carrera</b>",
                estilo_celda_bold
            ),
            Paragraph(
                normalizar_texto(
                    getattr(
                        solicitud,
                        "carrera",
                        "N/A"
                    )
                ),
                estilo_celda
            ),
        ],

        [
            Paragraph(
                "<b>Equipo</b>",
                estilo_celda_bold
            ),
            Paragraph(
                normalizar_texto(
                    solicitud.equipo
                ),
                estilo_celda
            ),
            Paragraph(
                "<b>Cantidad</b>",
                estilo_celda_bold
            ),
            Paragraph(
                normalizar_texto(
                    solicitud.cantidad
                ),
                estilo_celda
            ),
        ],

        [
            Paragraph(
                "<b>Fecha Registro</b>",
                estilo_celda_bold
            ),
            Paragraph(
                fecha_reg,
                estilo_celda
            ),
            Paragraph(
                "",
                estilo_celda
            ),
            Paragraph(
                "",
                estilo_celda
            ),
        ],
    ]

    t_principal = Table(
        tabla_data,
        colWidths=[
            110,
            160,
            110,
            160,
        ],
    )

    t_principal.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#CCCCCC"
                    ),
                ),

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor(
                        "#F2F2F2"
                    ),
                ),

                (
                    "BACKGROUND",
                    (2, 0),
                    (2, -1),
                    colors.HexColor(
                        "#F2F2F2"
                    ),
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    elementos.append(
        t_principal
    )

    elementos.append(
        Spacer(
            1,
            20
        )
    )

    estilo_pie = ParagraphStyle(
        "Pie",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        alignment=1,
        textColor=colors.gray,
    )

    elementos.append(
        Paragraph(
            "Documento generado automaticamente por el Sistema Institucional SEMGA.",
            estilo_pie,
        )
    )

    doc.build(
        elementos
    )

    return response


# ============================================================
# APROBAR
# ============================================================

@transaction.atomic
def aprobar_solicitud_equipo(
    request,
    id
):

    if not puede_editar_solicitudes(
        request.user
    ):

        return HttpResponseForbidden(
            "Acceso denegado."
        )

    solicitud = get_object_or_404(
        SolicitudEquipo,
        id=id
    )

    # Si ya está aprobada no volvemos a descontar.
    if solicitud.estado == "Aprobada":

        messages.warning(
            request,
            "Esta solicitud ya se encuentra aprobada."
        )

        return redirect(
            "lista_solicitudes_equipos"
        )

    # No se puede aprobar una solicitud devuelta
    # o rechazada directamente sin crear una nueva
    # operación.
    if solicitud.estado not in [
        "Pendiente"
    ]:

        messages.error(
            request,
            "Esta solicitud no puede ser aprobada "
            f"porque actualmente está '{solicitud.estado}'."
        )

        return redirect(
            "lista_solicitudes_equipos"
        )

    resultado = descontar_inventario(
        solicitud
    )

    if not resultado:

        messages.error(
            request,
            "No hay suficiente stock disponible "
            "para aprobar esta solicitud."
        )

        return redirect(
            "lista_solicitudes_equipos"
        )

    solicitud.estado = "Aprobada"

    solicitud.save(
        update_fields=[
            "estado"
        ]
    )

    # Notificación al estudiante.
    estudiante_user = User.objects.filter(
        Q(
            username__iexact=str(
                solicitud.estudiante
            )
        )
        |
        Q(
            perfil__rol__iexact="Estudiante",
            first_name__icontains=str(
                solicitud.estudiante
            ),
        )
    ).first()

    if estudiante_user:

        enviar_notificacion_y_correo(
            usuario=estudiante_user,
            titulo=(
                "Solicitud de Equipo: "
                "Aprobada 💻"
            ),
            mensaje=(
                f"Tu solicitud para el equipo "
                f"{solicitud.equipo} "
                f"ha sido Aprobada. "
                f"Cantidad aprobada: "
                f"{solicitud.cantidad}."
            ),
            url_destino=(
                "/solicitudes-equipos/"
            )
        )

    messages.success(
        request,
        (
            f"La solicitud #{solicitud.id} "
            "ha sido APROBADA exitosamente. "
            f"Se descontaron {solicitud.cantidad} "
            "unidad(es) del inventario."
        )
    )

    return redirect(
        "lista_solicitudes_equipos"
    )


# ============================================================
# RECHAZAR
# ============================================================

def rechazar_solicitud_equipo(
    request,
    id
):

    if not puede_editar_solicitudes(
        request.user
    ):

        return HttpResponseForbidden(
            "Acceso denegado."
        )

    solicitud = get_object_or_404(
        SolicitudEquipo,
        id=id
    )

    # Si ya estaba aprobada, no permitimos
    # rechazarla porque ya representa un préstamo.
    if solicitud.estado == "Aprobada":

        messages.error(
            request,
            "Una solicitud aprobada no puede ser "
            "rechazada. Debe registrarse como devuelta."
        )

        return redirect(
            "lista_solicitudes_equipos"
        )

    solicitud.estado = "Rechazada"

    solicitud.inventario_descontado = False

    solicitud.save(
        update_fields=[
            "estado",
            "inventario_descontado",
        ]
    )

    estudiante_user = User.objects.filter(
        Q(
            username__iexact=str(
                solicitud.estudiante
            )
        )
        |
        Q(
            perfil__rol__iexact="Estudiante",
            first_name__icontains=str(
                solicitud.estudiante
            ),
        )
    ).first()

    if estudiante_user:

        enviar_notificacion_y_correo(
            usuario=estudiante_user,
            titulo=(
                "Solicitud de Equipo: "
                "Rechazada 💻"
            ),
            mensaje=(
                f"Tu solicitud para el equipo "
                f"{solicitud.equipo} "
                "ha sido Rechazada."
            ),
            url_destino=(
                "/solicitudes-equipos/"
            )
        )

    messages.error(
        request,
        (
            f"La solicitud #{solicitud.id} "
            "ha sido RECHAZADA."
        )
    )

    return redirect(
        "lista_solicitudes_equipos"
    )


# ============================================================
# DEVOLVER
# ============================================================

@transaction.atomic
def devolver_solicitud_equipo(
    request,
    id
):

    if not puede_editar_solicitudes(
        request.user
    ):

        return HttpResponseForbidden(
            "Acceso denegado."
        )

    solicitud = get_object_or_404(
        SolicitudEquipo,
        id=id
    )

    if solicitud.estado != "Aprobada":

        messages.error(
            request,
            "Solo se puede devolver una solicitud "
            "que se encuentre aprobada."
        )

        return redirect(
            "lista_solicitudes_equipos"
        )

    devolver_inventario(
        solicitud
    )

    solicitud.estado = "Devuelta"

    solicitud.save(
        update_fields=[
            "estado"
        ]
    )

    estudiante_user = User.objects.filter(
        Q(
            username__iexact=str(
                solicitud.estudiante
            )
        )
        |
        Q(
            perfil__rol__iexact="Estudiante",
            first_name__icontains=str(
                solicitud.estudiante
            ),
        )
    ).first()

    if estudiante_user:

        enviar_notificacion_y_correo(
            usuario=estudiante_user,
            titulo=(
                "Equipo devuelto correctamente 💻"
            ),
            mensaje=(
                f"La devolución del equipo "
                f"{solicitud.equipo} "
                "ha sido registrada correctamente."
            ),
            url_destino=(
                "/solicitudes-equipos/"
            )
        )

    messages.success(
        request,
        (
            f"La solicitud #{solicitud.id} "
            "ha sido marcada como DEVUELTA. "
            f"Se devolvieron {solicitud.cantidad} "
            "unidad(es) al inventario."
        )
    )

    return redirect(
        "lista_solicitudes_equipos"
    )