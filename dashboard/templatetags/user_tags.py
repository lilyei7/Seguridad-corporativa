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
    Verifica si el usuario es superusuario o no tiene grupos (admin)
    Uso: {{ user|is_admin_or_superuser }}
    """
    if not user.is_authenticated:
        return False
    
    return user.is_superuser or not user.groups.exists()

@register.simple_tag
def user_role_display(user):
    """
    Retorna el rol del usuario para mostrar
    Uso: {% user_role_display user %}
    """
    if not user.is_authenticated:
        return "Invitado"
    
    if user.is_superuser:
        return "Administrador"
    
    if user.groups.exists():
        return user.groups.first().name
    
    return "Administrador"
