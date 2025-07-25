from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User, Group
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Guard, SecurityPoint, SecurityRoute, RoutePoint
from .forms import GuardForm, SecurityPointForm, SecurityRouteForm, GuardAssignmentForm


@login_required
def guard_list(request):
    """Vista para listar todos los vigilantes"""
    guards = Guard.objects.select_related('user').order_by('user__first_name', 'user__last_name')
    
    # Búsqueda
    search = request.GET.get('search')
    if search:
        guards = guards.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(employee_id__icontains=search)
        )
    
    # Filtros
    status = request.GET.get('status')
    if status == 'active':
        guards = guards.filter(status='activo')
    elif status == 'inactive':
        guards = guards.filter(status__in=['inactivo', 'suspendido'])
    
    context = {
        'guards': guards,
        'total_guards': Guard.objects.count(),
        'active_guards': Guard.objects.filter(status='activo').count(),
        'inactive_guards': Guard.objects.filter(status__in=['inactivo', 'suspendido']).count(),
    }
    
    return render(request, 'guards/guard_list.html', context)


@login_required
def guard_create(request):
    """Vista para crear un nuevo guard"""
    if request.method == 'POST':
        form = GuardForm(request.POST)
        if form.is_valid():
            guard = form.save()
            messages.success(request, f'Vigilante {guard.user.get_full_name()} registrado exitosamente')
            return redirect('dashboard:guards_list')
    else:
        form = GuardForm()
    
    context = {
        'form': form,
        'title': 'Registrar Nuevo Vigilante',
        'button_text': 'Registrar Vigilante'
    }
    
    return render(request, 'guards/guard_form.html', context)


@login_required
def guard_detail(request, guard_id):
    """Vista para ver detalles de un guard"""
    guard = get_object_or_404(Guard, id=guard_id)
    
    context = {
        'guard': guard,
        'title': f'Detalles de {guard.user.get_full_name()}'
    }
    
    return render(request, 'guards/guard_detail.html', context)


@login_required
def guard_edit(request, guard_id):
    """Vista para editar un guard"""
    guard = get_object_or_404(Guard, id=guard_id)
    
    if request.method == 'POST':
        form = GuardForm(request.POST, instance=guard)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vigilante {guard.user.get_full_name()} actualizado exitosamente')
            return redirect('dashboard:guards_list')
    else:
        form = GuardForm(instance=guard)
    
    context = {
        'form': form,
        'guard': guard,
        'title': f'Editar {guard.user.get_full_name()}',
        'button_text': 'Actualizar Vigilante'
    }
    
    return render(request, 'guards/guard_form.html', context)


@login_required
def toggle_guard_status(request, guard_id):
    """Vista AJAX para cambiar el estado de un guard"""
    if request.method == 'POST':
        import json
        guard = get_object_or_404(Guard, id=guard_id)
        
        # Obtener el nuevo estado del body de la petición
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            new_status = data.get('status', 'activo')
        else:
            # Si es un toggle simple, alternar entre activo e inactivo
            new_status = 'inactivo' if guard.status == 'activo' else 'activo'
        
        guard.status = new_status
        guard.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Vigilante {guard.get_status_display().lower()} exitosamente',
            'new_status': guard.status
        })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


# ================================
# VISTAS DE PUNTOS DE SEGURIDAD
# ================================

@login_required
def security_points_list(request):
    """Vista para listar todos los puntos de seguridad"""
    points = SecurityPoint.objects.all().order_by('priority', 'floor', 'name')
    
    # Filtros
    search = request.GET.get('search', '')
    floor_filter = request.GET.get('floor', '')
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('point_type', '')
    
    if search:
        points = points.filter(name__icontains=search) | points.filter(code__icontains=search)
    
    if floor_filter:
        points = points.filter(floor__icontains=floor_filter)
    
    if status_filter:
        points = points.filter(status=status_filter)
        
    if type_filter:
        points = points.filter(point_type=type_filter)
    
    # Estadísticas
    stats = {
        'total': SecurityPoint.objects.count(),
        'activos': SecurityPoint.objects.filter(status='activo').count(),
        'inactivos': SecurityPoint.objects.filter(status='inactivo').count(),
        'mantenimiento': SecurityPoint.objects.filter(status='mantenimiento').count(),
    }
    
    # Opciones para filtros
    floors = SecurityPoint.objects.values_list('floor', flat=True).distinct().order_by('floor')
    point_types = SecurityPoint.POINT_TYPE_CHOICES
    status_choices = SecurityPoint.POINT_STATUS_CHOICES
    
    context = {
        'points': points,
        'stats': stats,
        'search': search,
        'floor_filter': floor_filter,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'floors': floors,
        'point_types': point_types,
        'status_choices': status_choices,
    }
    
    return render(request, 'guards/security_points_list.html', context)


@login_required
def security_point_create(request):
    """Vista para crear un nuevo punto de seguridad"""
    if request.method == 'POST':
        form = SecurityPointForm(request.POST, request.FILES)
        if form.is_valid():
            point = form.save()
            messages.success(request, f'Punto de seguridad {point.code} - {point.name} creado exitosamente')
            return redirect('guards:security_points_list')
    else:
        form = SecurityPointForm()
    
    context = {
        'form': form,
        'title': 'Crear Nuevo Punto de Seguridad',
        'button_text': 'Crear Punto'
    }
    
    return render(request, 'guards/security_point_form.html', context)


@login_required
def security_point_detail(request, point_id):
    """Vista para ver los detalles de un punto de seguridad"""
    point = get_object_or_404(SecurityPoint, id=point_id)
    
    # Obtener estadísticas del punto
    recent_checks = point.pointcheck_set.order_by('-check_time')[:10]
    total_checks = point.pointcheck_set.count()
    last_check = point.pointcheck_set.order_by('-check_time').first()
    
    # Vigilantes asignados a este punto
    assigned_guards = Guard.objects.filter(assigned_points=point, status='activo')
    
    # Rutas que incluyen este punto
    related_routes = SecurityRoute.objects.filter(security_points=point)
    
    context = {
        'point': point,
        'recent_checks': recent_checks,
        'total_checks': total_checks,
        'last_check': last_check,
        'assigned_guards': assigned_guards,
        'related_routes': related_routes,
    }
    
    return render(request, 'guards/security_point_detail.html', context)


@login_required
def security_point_edit(request, point_id):
    """Vista para editar un punto de seguridad"""
    point = get_object_or_404(SecurityPoint, id=point_id)
    
    if request.method == 'POST':
        form = SecurityPointForm(request.POST, request.FILES, instance=point)
        if form.is_valid():
            point = form.save()
            messages.success(request, f'Punto de seguridad {point.code} - {point.name} actualizado exitosamente')
            return redirect('guards:security_point_detail', point_id=point.id)
    else:
        form = SecurityPointForm(instance=point)
    
    context = {
        'form': form,
        'point': point,
        'title': f'Editar Punto: {point.code} - {point.name}',
        'button_text': 'Actualizar Punto'
    }
    
    return render(request, 'guards/security_point_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def security_point_delete(request, point_id):
    """Vista para eliminar un punto de seguridad (AJAX)"""
    try:
        point = get_object_or_404(SecurityPoint, id=point_id)
        
        # Verificar si el punto tiene verificaciones recientes
        recent_checks = point.pointcheck_set.count()
        if recent_checks > 0:
            return JsonResponse({
                'success': False,
                'message': f'No se puede eliminar el punto. Tiene {recent_checks} verificaciones registradas.'
            })
        
        point_name = f"{point.code} - {point.name}"
        point.delete()
        
        messages.success(request, f'Punto de seguridad {point_name} eliminado exitosamente')
        return JsonResponse({
            'success': True,
            'message': f'Punto de seguridad {point_name} eliminado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar punto: {str(e)}'
        })


# ================================
# VISTAS DE RUTAS DE SEGURIDAD
# ================================

@login_required
def security_routes_list(request):
    """Vista para listar todas las rutas de seguridad"""
    routes = SecurityRoute.objects.all().order_by('name')
    
    # Filtros
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search:
        routes = routes.filter(name__icontains=search) | routes.filter(code__icontains=search)
    
    if status_filter:
        routes = routes.filter(status=status_filter)
    
    # Estadísticas
    stats = {
        'total': SecurityRoute.objects.count(),
        'activas': SecurityRoute.objects.filter(status='activa').count(),
        'inactivas': SecurityRoute.objects.filter(status='inactiva').count(),
        'temporales': SecurityRoute.objects.filter(status='temporal').count(),
    }
    
    context = {
        'routes': routes,
        'stats': stats,
        'search': search,
        'status_filter': status_filter,
        'status_choices': SecurityRoute.ROUTE_STATUS_CHOICES,
    }
    
    return render(request, 'guards/security_routes_list.html', context)


@login_required
def security_route_create(request):
    """Vista para crear una nueva ruta de seguridad"""
    if request.method == 'POST':
        form = SecurityRouteForm(request.POST)
        if form.is_valid():
            route = form.save()
            messages.success(request, f'Ruta de seguridad {route.code} - {route.name} creada exitosamente')
            return redirect('guards:security_route_edit_points', route_id=route.id)
    else:
        form = SecurityRouteForm()
    
    context = {
        'form': form,
        'title': 'Crear Nueva Ruta de Seguridad',
        'button_text': 'Crear Ruta'
    }
    
    return render(request, 'guards/security_route_form.html', context)


@login_required
def security_route_detail(request, route_id):
    """Vista para ver los detalles de una ruta de seguridad"""
    route = get_object_or_404(SecurityRoute, id=route_id)
    
    # Obtener puntos de la ruta ordenados
    route_points = RoutePoint.objects.filter(route=route).order_by('order')
    
    # Vigilantes asignados a esta ruta
    assigned_guards = Guard.objects.filter(assigned_routes=route, status='activo')
    
    # Rondines recientes
    recent_patrols = route.patrolround_set.order_by('-start_time')[:10]
    
    context = {
        'route': route,
        'route_points': route_points,
        'assigned_guards': assigned_guards,
        'recent_patrols': recent_patrols,
    }
    
    return render(request, 'guards/security_route_detail.html', context)


@login_required
def security_route_edit(request, route_id):
    """Vista para editar una ruta de seguridad"""
    route = get_object_or_404(SecurityRoute, id=route_id)
    
    if request.method == 'POST':
        form = SecurityRouteForm(request.POST, instance=route)
        if form.is_valid():
            route = form.save()
            messages.success(request, f'Ruta de seguridad {route.code} - {route.name} actualizada exitosamente')
            return redirect('guards:security_route_detail', route_id=route.id)
    else:
        form = SecurityRouteForm(instance=route)
    
    context = {
        'form': form,
        'route': route,
        'title': f'Editar Ruta: {route.code} - {route.name}',
        'button_text': 'Actualizar Ruta'
    }
    
    return render(request, 'guards/security_route_form.html', context)


@login_required
def security_route_edit_points(request, route_id):
    """Vista para editar los puntos de una ruta"""
    route = get_object_or_404(SecurityRoute, id=route_id)
    
    if request.method == 'POST':
        # Procesar la actualización de puntos
        points_data = request.POST.getlist('points')
        
        # Eliminar puntos existentes
        RoutePoint.objects.filter(route=route).delete()
        
        # Agregar nuevos puntos
        for i, point_id in enumerate(points_data, 1):
            if point_id:
                point = SecurityPoint.objects.get(id=point_id)
                RoutePoint.objects.create(
                    route=route,
                    security_point=point,
                    order=i,
                    estimated_time_minutes=5  # Valor por defecto
                )
        
        messages.success(request, f'Puntos de la ruta {route.code} actualizados exitosamente')
        return redirect('guards:security_route_detail', route_id=route.id)
    
    # Obtener puntos actuales y disponibles
    current_points = RoutePoint.objects.filter(route=route).order_by('order')
    available_points = SecurityPoint.objects.filter(status='activo').order_by('floor', 'name')
    
    context = {
        'route': route,
        'current_points': current_points,
        'available_points': available_points,
    }
    
    return render(request, 'guards/security_route_edit_points.html', context)


# ================================
# VISTAS DE ASIGNACIÓN
# ================================

@login_required
def guard_assignments(request):
    """Vista para gestionar asignaciones de vigilantes"""
    guards = Guard.objects.filter(status='activo').order_by('user__first_name')
    
    context = {
        'guards': guards,
    }
    
    return render(request, 'guards/guard_assignments.html', context)


@login_required
def guard_assignment_edit(request, guard_id):
    """Vista para editar asignaciones de un vigilante"""
    guard = get_object_or_404(Guard, id=guard_id)
    
    if request.method == 'POST':
        form = GuardAssignmentForm(request.POST, instance=guard)
        if form.is_valid():
            form.save()
            messages.success(request, f'Asignaciones de {guard.full_name} actualizadas exitosamente')
            return redirect('guards:guard_assignments')
    else:
        form = GuardAssignmentForm(instance=guard)
    
    context = {
        'form': form,
        'guard': guard,
        'title': f'Asignaciones: {guard.full_name}',
        'button_text': 'Actualizar Asignaciones'
    }
    
    return render(request, 'guards/guard_assignment_form.html', context)
