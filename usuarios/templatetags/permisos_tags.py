from django import template
from usuarios.permisos import (
    puede_agregar_inventario,
    puede_editar_inventario,
    puede_eliminar_inventario,
    puede_aprobar_solicitudes,
    puede_editar_solicitudes,
    puede_eliminar_solicitudes,
    puede_gestionar_sedes_carreras,
    es_estudiante,
)

register = template.Library()

@register.filter
def can_approve_requests(user):
    return puede_aprobar_solicitudes(user)

@register.filter
def can_edit_requests(user):
    return puede_editar_solicitudes(user)

@register.filter
def can_delete_requests(user):
    return puede_eliminar_solicitudes(user)

@register.filter
def can_add_inventory(user):
    return puede_agregar_inventario(user)

@register.filter
def can_edit_inventory(user):
    return puede_editar_inventario(user)

@register.filter
def can_delete_inventory(user):
    return puede_eliminar_inventario(user)

@register.filter
def can_manage_locations(user):
    """
    Retorna True solo si puede ver y gestionar Sedes y Carreras
    (Superadmin y Admin Talleres).
    """
    return puede_gestionar_sedes_carreras(user)

@register.filter
def is_student(user):
    return es_estudiante(user)