from django import template
from accounts.models import UserRole, Notification

register = template.Library()

@register.filter
def in_group(user, group_name):
    """
    Verifica si el usuario pertenece a un grupo específico
    Uso: {{ user|in_group:"Inquilinos" }}
    """
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()

@register.filter
def has_role(user, role_name):
    """
    Verifica si el usuario tiene un rol específico
    Uso: {{ user|has_role:"admin" }}
    """
    if not user.is_authenticated:
        return False
    
    try:
        user_role = getattr(user, 'user_role', None)
        if user_role and user_role.is_active:
            return user_role.role == role_name
        return False
    except Exception:
        return False

@register.filter
def is_admin(user):
    """
    Verifica si el usuario es admin
    Uso: {{ user|is_admin }}
    """
    return has_role(user, 'admin') or user.is_superuser

@register.filter
def is_tenant(user):
    """
    Verifica si el usuario es inquilino
    Uso: {{ user|is_tenant }}
    """
    return has_role(user, 'tenant')

@register.filter
def is_guard(user):
    """
    Verifica si el usuario es vigilante
    Uso: {{ user|is_guard }}
    """
    return has_role(user, 'guard')

@register.filter
def is_maintenance(user):
    """
    Verifica si el usuario es personal de mantenimiento
    Uso: {{ user|is_maintenance }}
    """
    return has_role(user, 'maintenance')

@register.filter
def is_reception(user):
    """
    Verifica si el usuario es recepcionista
    Uso: {{ user|is_reception }}
    """
    return has_role(user, 'reception')

@register.filter
def get_user_role(user):
    """
    Obtiene el rol del usuario
    Uso: {{ user|get_user_role }}
    """
    if not user.is_authenticated:
        return None
    
    try:
        user_role = getattr(user, 'user_role', None)
        if user_role and user_role.is_active:
            return user_role
        return None
    except Exception:
        return None

@register.filter
def get_user_role_display(user):
    """
    Obtiene el nombre del rol del usuario para mostrar
    Uso: {{ user|get_user_role_display }}
    """
    if not user.is_authenticated:
        return "Invitado"
    
    if user.is_superuser:
        return "Superusuario"
    
    user_role = get_user_role(user)
    if user_role:
        return user_role.get_role_display()
    
    return "Sin rol asignado"

@register.filter
def get_tenant_info(user):
    """
    Obtiene la información del inquilino del usuario
    Uso: {{ user|get_tenant_info }}
    """
    if not user.is_authenticated:
        return None
    
    user_role = get_user_role(user)
    if user_role and user_role.role == 'tenant' and user_role.tenant_profile:
        return user_role.tenant_profile
    
    return None

@register.filter
def unread_notifications_count(user):
    """
    Obtiene el número de notificaciones no leídas
    Uso: {{ user|unread_notifications_count }}
    """
    if not user.is_authenticated:
        return 0
    
    return Notification.objects.filter(recipient=user, is_read=False).count()

@register.simple_tag
def get_notifications(user, limit=5):
    """
    Obtiene las últimas notificaciones del usuario
    Uso: {% get_notifications user 5 as recent_notifications %}
    """
    if not user.is_authenticated:
        return []
    
    return Notification.objects.filter(
        recipient=user
    ).order_by('-created_at')[:limit]

@register.simple_tag
def can_access_admin(user):
    """
    Verifica si el usuario puede acceder a funciones de administración
    Uso: {% can_access_admin user as can_admin %}
    """
    return is_admin(user)

@register.simple_tag
def can_manage_visits(user):
    """
    Verifica si el usuario puede gestionar visitas
    Uso: {% can_manage_visits user as can_manage %}
    """
    return has_role(user, 'admin') or has_role(user, 'guard') or has_role(user, 'reception')

@register.simple_tag
def can_create_visits(user):
    """
    Verifica si el usuario puede crear visitas
    Uso: {% can_create_visits user as can_create %}
    """
    return has_role(user, 'admin') or has_role(user, 'tenant') or has_role(user, 'reception')

@register.inclusion_tag('components/user_role_badge.html')
def user_role_badge(user):
    """
    Renderiza un badge con el rol del usuario
    Uso: {% user_role_badge user %}
    """
    user_role = get_user_role(user)
    role_colors = {
        'admin': 'bg-red-100 text-red-800',
        'tenant': 'bg-purple-100 text-purple-800',
        'guard': 'bg-green-100 text-green-800',
        'maintenance': 'bg-orange-100 text-orange-800',
        'reception': 'bg-blue-100 text-blue-800',
    }
    
    return {
        'user': user,
        'user_role': user_role,
        'role_display': get_user_role_display(user),
        'role_color': role_colors.get(user_role.role if user_role else '', 'bg-gray-100 text-gray-800'),
        'is_superuser': user.is_superuser,
    }