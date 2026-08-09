from .permisos import (
    puede_crear_usuarios,
    puede_agregar_inventario,
    puede_editar_inventario,
    puede_eliminar_inventario,
    puede_aprobar_solicitudes,
    puede_editar_solicitudes,
    puede_eliminar_solicitudes,
    es_superadmin,
    es_admin_talleres,
    es_coord_carrera,
    es_coord_talleres,
    es_docente,
    es_estudiante,
)

def permisos_context(request):
    """
    Inyecta las funciones de permisos directamente a todas las plantillas HTML.
    """
    if not request.user.is_authenticated:
        return {}

    return {
        # Permisos de acciones
        'puede_crear_usuarios': puede_crear_usuarios(request.user),
        'puede_agregar_inventario': puede_agregar_inventario(request.user),
        'puede_editar_inventario': puede_editar_inventario(request.user),
        'puede_eliminar_inventario': puede_eliminar_inventario(request.user),
        'puede_aprobar_solicitudes': puede_aprobar_solicitudes(request.user),
        'puede_editar_solicitudes': puede_editar_solicitudes(request.user),
        'puede_eliminar_solicitudes': puede_eliminar_solicitudes(request.user),
        # Roles directos (para el menú/dashboard)
        'es_superadmin': es_superadmin(request.user),
        'es_admin_talleres': es_admin_talleres(request.user),
        'es_coord_carrera': es_coord_carrera(request.user),
        'es_coord_talleres': es_coord_talleres(request.user),
        'es_docente': es_docente(request.user),
        'es_estudiante': es_estudiante(request.user),
    }