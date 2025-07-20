from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from tenants.models import Tenant
from guards.models import Guard
from .forms import CustomUserCreationForm, UserEditForm, TenantEditForm, GuardEditForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                
                # Redireccionar según el tipo de usuario
                if user.is_superuser:
                    return redirect('dashboard:admin_panel')
                elif user.groups.filter(name='Vigilantes').exists():
                    return redirect('dashboard:guard_panel')
                elif user.groups.filter(name='Inquilinos').exists():
                    return redirect('dashboard:tenant_panel')
                else:
                    # Usuario sin grupo específico, redirigir al panel de admin
                    return redirect('dashboard:admin_panel')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor ingresa usuario y contraseña.')
    
    return render(request, 'login.html')

@login_required
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


# ========== GESTIÓN DE USUARIOS ==========

@login_required
def users_list(request):
    """Vista para listar todos los usuarios del sistema"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard:index')
    
    users = User.objects.all().order_by('username')
    
    # Filtros
    search = request.GET.get('search', '')
    group_filter = request.GET.get('group', '')
    status_filter = request.GET.get('status', '')
    
    if search:
        users = users.filter(
            username__icontains=search
        ) | users.filter(
            first_name__icontains=search
        ) | users.filter(
            last_name__icontains=search
        ) | users.filter(
            email__icontains=search
        )
    
    if group_filter:
        users = users.filter(groups__name=group_filter)
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Estadísticas
    stats = {
        'total': User.objects.count(),
        'activos': User.objects.filter(is_active=True).count(),
        'inactivos': User.objects.filter(is_active=False).count(),
        'administradores': User.objects.filter(is_superuser=True).count(),
        'vigilantes': User.objects.filter(groups__name='Vigilantes').count(),
        'inquilinos': User.objects.filter(groups__name='Inquilinos').count(),
    }
    
    groups = Group.objects.all()
    
    context = {
        'users': users,
        'stats': stats,
        'groups': groups,
        'search': search,
        'group_filter': group_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'accounts/users_list.html', context)


@login_required
def user_create(request):
    """Vista para crear un nuevo usuario"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'Usuario {user.username} creado exitosamente.')
                return redirect('accounts:user_detail', user.id)
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'accounts/user_create_simple.html', context)


@login_required
def user_detail(request, user_id):
    """Vista para ver detalles de un usuario"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard:index')
    
    user = get_object_or_404(User, id=user_id)
    
    # Obtener información adicional
    tenant = None
    guard = None
    
    try:
        tenant = Tenant.objects.get(usuario=user)
    except Tenant.DoesNotExist:
        pass
    
    try:
        guard = Guard.objects.get(user=user)
    except Guard.DoesNotExist:
        pass
    
    context = {
        'user_detail': user,
        'tenant': tenant,
        'guard': guard,
    }
    
    return render(request, 'accounts/user_detail.html', context)


@login_required
def user_edit(request, user_id):
    """Vista para editar un usuario"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard:index')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        
        # Cambiar contraseña si se proporciona
        new_password = request.POST.get('new_password')
        if new_password:
            if len(new_password) >= 6:
                user.set_password(new_password)
            else:
                messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
                return render(request, 'accounts/user_edit.html', {'user_detail': user})
        
        user.save()
        messages.success(request, 'Usuario actualizado exitosamente.')
        return redirect('accounts:user_detail', user_id=user.id)
    
    context = {
        'user_detail': user,
    }
    
    return render(request, 'accounts/user_edit.html', context)


@login_required
def toggle_user_status(request, user_id):
    """Vista para activar/desactivar un usuario"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'No tienes permisos'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    
    if user.id == request.user.id:
        return JsonResponse({'error': 'No puedes desactivarte a ti mismo'}, status=400)
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'activado' if user.is_active else 'desactivado'
    messages.success(request, f'Usuario {user.username} {status} exitosamente.')
    
    return JsonResponse({'success': True, 'is_active': user.is_active})


@login_required
def assign_roles(request):
    """Vista para asignar roles masivamente"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard:index')
    
    users = User.objects.all().order_by('username')
    groups = Group.objects.all()
    
    context = {
        'users': users,
        'groups': groups,
    }
    
    return render(request, 'accounts/assign_roles.html', context)


@login_required
def assign_user_role(request, user_id):
    """Vista para asignar rol a un usuario específico"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'No tienes permisos'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        action = request.POST.get('action')  # 'add' o 'remove'
        
        if group_id:
            try:
                group = Group.objects.get(id=group_id)
                
                if action == 'add':
                    user.groups.add(group)
                    messages.success(request, f'Rol {group.name} asignado a {user.username}.')
                elif action == 'remove':
                    user.groups.remove(group)
                    messages.success(request, f'Rol {group.name} removido de {user.username}.')
                
                return JsonResponse({'success': True})
                
            except Group.DoesNotExist:
                return JsonResponse({'error': 'Grupo no encontrado'}, status=404)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)
