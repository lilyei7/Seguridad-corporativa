from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(allowed_roles):
    """
    Decorador para vistas que requieren roles específicos
    
    @role_required(['admin', 'tenant'])
    def my_view(request):
        pass
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            try:
                user_role = request.user.role_profile.role
                if user_role not in allowed_roles:
                    messages.error(request, "No tienes permisos para acceder a esta sección.")
                    return redirect('dashboard:index')
                return view_func(request, *args, **kwargs)
            except AttributeError:
                messages.error(request, "Tu cuenta no tiene un rol asignado. Contacta al administrador.")
                return redirect('dashboard:index')
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Decorador para vistas que solo pueden acceder administradores"""
    return role_required(['admin'])(view_func)


def tenant_required(view_func):
    """Decorador para vistas de inquilinos"""
    return role_required(['admin', 'tenant'])(view_func)


def guard_required(view_func):
    """Decorador para vistas de vigilantes"""
    return role_required(['admin', 'guard'])(view_func)


def maintenance_required(view_func):
    """Decorador para vistas de mantenimiento"""
    return role_required(['admin', 'maintenance'])(view_func)


class RoleRequiredMixin:
    """Mixin para vistas basadas en clases que requieren roles específicos"""
    allowed_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            user_role = request.user.role_profile.role
            if user_role not in self.allowed_roles:
                raise PermissionDenied("No tienes permisos para acceder a esta sección.")
        except AttributeError:
            raise PermissionDenied("Tu cuenta no tiene un rol asignado.")
        
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    """Mixin para vistas que solo pueden acceder administradores"""
    allowed_roles = ['admin']


class TenantRequiredMixin(RoleRequiredMixin):
    """Mixin para vistas de inquilinos"""
    allowed_roles = ['admin', 'tenant']


class GuardRequiredMixin(RoleRequiredMixin):
    """Mixin para vistas de vigilantes"""
    allowed_roles = ['admin', 'guard']


class MaintenanceRequiredMixin(RoleRequiredMixin):
    """Mixin para vistas de mantenimiento"""
    allowed_roles = ['admin', 'maintenance']


def get_user_role(user):
    """Función auxiliar para obtener el rol de un usuario"""
    try:
        return user.role_profile.role
    except AttributeError:
        return None


def user_can_view_item(user, item_owner_id=None, required_roles=None):
    """
    Función para verificar si un usuario puede ver un elemento específico
    
    Args:
        user: Usuario actual
        item_owner_id: ID del usuario propietario del item (opcional)
        required_roles: Lista de roles que pueden ver el item
    
    Returns:
        bool: True si puede ver, False si no
    """
    user_role = get_user_role(user)
    
    if not user_role:
        return False
    
    # Admin puede ver todo
    if user_role == 'admin':
        return True
    
    # Si se especifican roles requeridos, verificar
    if required_roles and user_role not in required_roles:
        return False
    
    # Si hay propietario específico, verificar si es el mismo usuario
    if item_owner_id and user.id != item_owner_id:
        return False
    
    return True


def filter_queryset_by_role(user, queryset, owner_field='user'):
    """
    Filtrar un queryset basado en el rol del usuario
    
    Args:
        user: Usuario actual
        queryset: QuerySet a filtrar
        owner_field: Campo que identifica al propietario
    
    Returns:
        QuerySet filtrado
    """
    user_role = get_user_role(user)
    
    # Admin puede ver todo
    if user_role == 'admin':
        return queryset
    
    # Otros usuarios solo pueden ver sus propios elementos
    filter_kwargs = {owner_field: user}
    return queryset.filter(**filter_kwargs)
