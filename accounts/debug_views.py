from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from accounts.models import UserRole
from tenants.models import Tenant


@login_required
def debug_user_info(request):
    """Vista de debug para mostrar información completa del usuario"""
    user = request.user
    
    # Información básica del usuario
    user_info = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.get_full_name(),
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
        'is_active': user.is_active,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
    }
    
    # Información del rol
    role_info = None
    try:
        user_role = user.user_role
        role_info = {
            'id': user_role.id,
            'role': user_role.role,
            'role_display': user_role.get_role_display(),
            'is_active': user_role.is_active,
            'created_at': user_role.created_at,
            'updated_at': user_role.updated_at,
            'tenant_profile_id': user_role.tenant_profile.id if user_role.tenant_profile else None,
            'guard_profile_id': user_role.guard_profile.id if user_role.guard_profile else None,
        }
    except UserRole.DoesNotExist:
        role_info = {'error': 'No UserRole found'}
    except Exception as e:
        role_info = {'error': str(e)}
    
    # Información de grupos
    groups_info = [
        {
            'id': group.id,
            'name': group.name,
        }
        for group in user.groups.all()
    ]
    
    # Información de tenant si es inquilino
    tenant_info = None
    if role_info and role_info.get('role') == 'tenant':
        try:
            if role_info.get('tenant_profile_id'):
                tenant = user.user_role.tenant_profile
            else:
                # Buscar tenant por otros métodos
                tenant = Tenant.objects.filter(assigned_user=user).first()
                if not tenant and user.email:
                    tenant = Tenant.objects.filter(contact_email=user.email).first()
            
            if tenant:
                tenant_info = {
                    'id': tenant.id,
                    'tenant_name': tenant.tenant_name,
                    'contact_person': tenant.contact_person,
                    'contact_email': tenant.contact_email,
                    'numero_oficina': tenant.numero_oficina,
                    'tipo_oficina': tenant.tipo_oficina,
                    'tipo_oficina_display': tenant.get_tipo_oficina_display(),
                    'assigned_user_id': tenant.assigned_user.id if tenant.assigned_user else None,
                    'assigned_user_username': tenant.assigned_user.username if tenant.assigned_user else None,
                    'is_active': tenant.is_active,
                }
            else:
                tenant_info = {'error': 'No Tenant found'}
        except Exception as e:
            tenant_info = {'error': str(e)}
    
    # Estadísticas adicionales
    stats = {
        'total_users': User.objects.count(),
        'total_tenants': Tenant.objects.count(),
        'total_user_roles': UserRole.objects.count(),
        'users_with_roles': UserRole.objects.filter(is_active=True).count(),
        'tenant_users': UserRole.objects.filter(role='tenant', is_active=True).count(),
    }
    
    context = {
        'user_info': user_info,
        'role_info': role_info,
        'groups_info': groups_info,
        'tenant_info': tenant_info,
        'stats': stats,
        'debug_mode': True,
    }
    
    # Si es una petición JSON, devolver los datos
    if request.headers.get('Content-Type') == 'application/json' or request.GET.get('format') == 'json':
        return JsonResponse(context, indent=2)
    
    return render(request, 'accounts/debug_user_info.html', context)
