from usuarios.models import Perfil


def obtener_rol(usuario):
    """
    Devuelve el rol del usuario.
    """
    if not usuario or not usuario.is_authenticated:
        return None

    try:
        return usuario.perfil.rol
    except Perfil.DoesNotExist:
        return None


# ==============================
# ROLES INDIVIDUALES
# ==============================

def es_superadmin(usuario):
    return usuario.is_superuser or obtener_rol(usuario) == "Superadministrador"


def es_admin_talleres(usuario):
    return obtener_rol(usuario) == "Administrador Talleres"


def es_coord_carrera(usuario):
    return obtener_rol(usuario) == "Coordinador Carrera"


def es_coord_talleres(usuario):
    return obtener_rol(usuario) == "Coordinador Talleres"


def es_docente(usuario):
    return obtener_rol(usuario) == "Docente"


def es_estudiante(usuario):
    return obtener_rol(usuario) == "Estudiante"


# ======================================
# PERMISOS DEL SISTEMA
# ======================================

def puede_crear_usuarios(usuario):
    return es_superadmin(usuario) or es_admin_talleres(usuario)


# Solo Superadministrador y Administrador Talleres pueden editar o eliminar inventario / herramientas
def puede_eliminar_inventario(usuario):
    return es_superadmin(usuario) or es_admin_talleres(usuario)


def puede_editar_inventario(usuario):
    return es_superadmin(usuario) or es_admin_talleres(usuario)


def puede_agregar_inventario(usuario):
    return (
        es_superadmin(usuario)
        or es_admin_talleres(usuario)
        or es_coord_carrera(usuario)
        or es_coord_talleres(usuario)
        or es_docente(usuario)
    )


# Permiso para gestionar (ver, crear, editar, eliminar) Sedes y Carreras
# Prohibido para Coordinador de Talleres, Docentes y Estudiantes
def puede_gestionar_sedes_carreras(usuario):
    return es_superadmin(usuario) or es_admin_talleres(usuario)


def puede_aprobar_solicitudes(usuario):
    return (
        es_superadmin(usuario)
        or es_admin_talleres(usuario)
        or es_coord_carrera(usuario)
        or es_coord_talleres(usuario)
    )


def puede_editar_solicitudes(usuario):
    return (
        es_superadmin(usuario)
        or es_admin_talleres(usuario)
        or es_coord_carrera(usuario)
    )


def puede_eliminar_solicitudes(usuario):
    return (
        es_superadmin(usuario)
        or es_admin_talleres(usuario)
        or es_coord_carrera(usuario)
    )


def puede_editar_biometria(usuario):
    if es_estudiante(usuario):
        return not (hasattr(usuario, "biometria") and usuario.biometria.foto)
    return True