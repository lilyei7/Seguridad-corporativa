from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter
def has_group(user, group_name):
    """
    Verifica si el usuario pertenece a un grupo específico
    Uso: {{ user|has_group:"Vigilantes" }}
    """
    if not user.is_authenticated:
        return False
    
    try:
        group = Group.objects.get(name=group_name)
        return group in user.groups.all()
    except Group.DoesNotExist:
        return False

@register.filter
def is_admin_or_superuser(user):
    """
    Verifica si el usuario es administrador o superusuario
    Uso: {{ user|is_admin_or_superuser }}
    """
    if not user.is_authenticated:
        return False
    
    return user.is_superuser or user.groups.filter(name__in=['Administradores', 'Admin']).exists()

@register.filter
def is_guard(user):
    """
    Verifica si el usuario es vigilante
    Uso: {{ user|is_guard }}
    """
    if not user.is_authenticated:
        return False
    
    return user.groups.filter(name='Vigilantes').exists()

@register.filter
def is_tenant(user):
    """
    Verifica si el usuario es inquilino
    Uso: {{ user|is_tenant }}
    """
    if not user.is_authenticated:
        return False
    
    return user.groups.filter(name='Inquilinos').exists()
