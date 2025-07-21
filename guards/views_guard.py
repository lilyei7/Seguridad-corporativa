from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from accounts.decorators import guard_required
from accounts.models import Notification
from guards.models import Guard, SecurityPoint, PatrolRoute, SecurityCamera, IncidentReport
from maintenance.models import MaintenanceRequest
from django.db.models import Q, Count


@guard_required
def guard_dashboard(request):
    """Dashboard específico para vigilantes"""
    context = {}
    
    try:
        # Obtener perfil del vigilante
        if hasattr(request.user, 'role_profile') and request.user.role_profile.guard_profile:
            guard = request.user.role_profile.guard_profile
            context['guard'] = guard
            
            # Estadísticas del vigilante
            context['stats'] = {
                'assigned_points': guard.assigned_points.filter(status='activo').count(),
                'today_reports': IncidentReport.objects.filter(
                    reported_by=request.user,
                    created_at__date=timezone.now().date()
                ).count(),
                'pending_maintenance': MaintenanceRequest.objects.filter(
                    created_by=request.user,
                    status='pendiente'
                ).count(),
                'unread_notifications': request.user.notifications.filter(
                    is_read=False
                ).count(),
            }
            
            # Puntos de seguridad asignados
            context['assigned_points'] = guard.assigned_points.filter(
                status='activo'
            ).order_by('priority')
            
            # Rutas de patrullaje de hoy
            context['todays_routes'] = PatrolRoute.objects.filter(
                assigned_guard=guard,
                scheduled_date=timezone.now().date()
            ).order_by('scheduled_time')
            
            # Reportes de incidentes recientes
            context['recent_incidents'] = IncidentReport.objects.filter(
                reported_by=request.user
            ).order_by('-created_at')[:5]
            
            # Notificaciones recientes
            context['recent_notifications'] = request.user.notifications.filter(
                is_read=False
            ).order_by('-created_at')[:5]
            
        else:
            messages.error(request, "No tienes un perfil de vigilante asociado. Contacta al administrador.")
            return redirect('dashboard:index')
    
    except Exception as e:
        messages.error(request, f"Error al cargar el dashboard: {str(e)}")
        return redirect('dashboard:index')
    
    return render(request, 'guards/dashboard.html', context)


@guard_required
def guard_security_points(request):
    """Vista de puntos de seguridad asignados al vigilante"""
    guard = request.user.role_profile.guard_profile
    
    # Puntos asignados a este vigilante
    assigned_points = guard.assigned_points.all().order_by('priority')
    
    # Todos los puntos (para referencia, pero no puede modificar los no asignados)
    all_points = SecurityPoint.objects.all().order_by('priority')
    
    context = {
        'guard': guard,
        'assigned_points': assigned_points,
        'all_points': all_points,
        'can_modify_points': False,  # Solo admin puede modificar asignaciones
    }
    
    return render(request, 'guards/security_points.html', context)


@guard_required
def guard_cameras(request):
    """Vista de cámaras de seguridad para vigilantes"""
    guard = request.user.role_profile.guard_profile
    
    # Cámaras de los puntos asignados al vigilante
    assigned_points = guard.assigned_points.all()
    cameras = SecurityCamera.objects.filter(
        location__in=[point.location for point in assigned_points]
    ).order_by('name')
    
    # Si no hay restricción por puntos, mostrar todas (ajustar según necesidades)
    if not cameras.exists():
        cameras = SecurityCamera.objects.filter(status='activa').order_by('name')
    
    context = {
        'guard': guard,
        'cameras': cameras,
        'assigned_points': assigned_points,
    }
    
    return render(request, 'guards/cameras.html', context)


@guard_required
def create_incident_report(request):
    """Crear nuevo reporte de incidente"""
    guard = request.user.role_profile.guard_profile
    
    if request.method == 'POST':
        try:
            incident = IncidentReport.objects.create(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                incident_type=request.POST.get('incident_type'),
                severity=request.POST.get('severity'),
                location=request.POST.get('location'),
                occurred_at=request.POST.get('occurred_at'),
                reported_by=request.user,
                status='abierto'
            )
            
            # Notificar a administradores basado en severidad
            priority_map = {
                'low': 'medium',
                'medium': 'high',
                'high': 'urgent',
                'critical': 'urgent'
            }
            
            Notification.send_incident_report(
                sender=request.user,
                title=incident.title,
                message=f"Reporte de incidente de {guard.nombre_completo}: {incident.description}",
                priority=priority_map.get(incident.severity, 'medium')
            )
            
            messages.success(request, "Reporte de incidente creado exitosamente.")
            return redirect('guards:incident_reports')
            
        except Exception as e:
            messages.error(request, f"Error al crear el reporte: {str(e)}")
    
    # Obtener puntos asignados para seleccionar ubicación
    assigned_points = guard.assigned_points.all()
    
    context = {
        'guard': guard,
        'assigned_points': assigned_points,
        'incident_types': IncidentReport.INCIDENT_TYPE_CHOICES,
        'severity_choices': IncidentReport.SEVERITY_CHOICES,
    }
    
    return render(request, 'guards/create_incident_report.html', context)


@guard_required
def guard_incident_reports(request):
    """Vista de reportes de incidentes del vigilante"""
    reports = IncidentReport.objects.filter(
        reported_by=request.user
    ).order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    severity_filter = request.GET.get('severity')
    if severity_filter:
        reports = reports.filter(severity=severity_filter)
    
    context = {
        'reports': reports,
        'status_choices': IncidentReport.STATUS_CHOICES,
        'severity_choices': IncidentReport.SEVERITY_CHOICES,
    }
    
    return render(request, 'guards/incident_reports.html', context)


@guard_required
def guard_patrol_routes(request):
    """Vista de rutas de patrullaje asignadas"""
    guard = request.user.role_profile.guard_profile
    
    # Rutas de hoy
    today_routes = PatrolRoute.objects.filter(
        assigned_guard=guard,
        scheduled_date=timezone.now().date()
    ).order_by('scheduled_time')
    
    # Rutas de la semana
    week_routes = PatrolRoute.objects.filter(
        assigned_guard=guard,
        scheduled_date__gte=timezone.now().date(),
        scheduled_date__lt=timezone.now().date() + timezone.timedelta(days=7)
    ).order_by('scheduled_date', 'scheduled_time')
    
    context = {
        'guard': guard,
        'today_routes': today_routes,
        'week_routes': week_routes,
    }
    
    return render(request, 'guards/patrol_routes.html', context)


@guard_required
def complete_patrol_check(request, route_id):
    """Marcar un punto de patrullaje como completado"""
    if request.method == 'POST':
        try:
            route = get_object_or_404(
                PatrolRoute, 
                id=route_id, 
                assigned_guard=request.user.role_profile.guard_profile
            )
            
            # Crear registro de verificación
            # Aquí podrías tener un modelo PatrolCheck
            
            messages.success(request, f"Punto {route.security_point.name} verificado exitosamente.")
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@guard_required
def guard_maintenance_requests(request):
    """Solicitudes de mantenimiento creadas por el vigilante"""
    requests = MaintenanceRequest.objects.filter(
        created_by=request.user
    ).order_by('-created_at')
    
    context = {
        'maintenance_requests': requests,
        'can_create_requests': True,
    }
    
    return render(request, 'guards/maintenance_requests.html', context)


@guard_required
def create_guard_maintenance_request(request):
    """Crear solicitud de mantenimiento como vigilante"""
    guard = request.user.role_profile.guard_profile
    
    if request.method == 'POST':
        try:
            maintenance_request = MaintenanceRequest.objects.create(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                category=request.POST.get('category'),
                priority=request.POST.get('priority', 'medium'),
                location=request.POST.get('location'),
                created_by=request.user,
                status='pendiente'
            )
            
            # Notificar a administradores
            Notification.send_maintenance_request(
                sender=request.user,
                title=maintenance_request.title,
                message=f"Solicitud de mantenimiento del vigilante {guard.nombre_completo}: {maintenance_request.description}"
            )
            
            messages.success(request, "Solicitud de mantenimiento enviada exitosamente.")
            return redirect('guards:maintenance_requests')
            
        except Exception as e:
            messages.error(request, f"Error al crear la solicitud: {str(e)}")
    
    # Obtener puntos asignados para seleccionar ubicación
    assigned_points = guard.assigned_points.all()
    
    context = {
        'guard': guard,
        'assigned_points': assigned_points,
        'categories': MaintenanceRequest.CATEGORY_CHOICES,
        'priorities': MaintenanceRequest.PRIORITY_CHOICES,
    }
    
    return render(request, 'guards/create_maintenance_request.html', context)


@guard_required
def guard_notifications(request):
    """Ver notificaciones del vigilante"""
    notifications = request.user.notifications.order_by('-created_at')
    
    # Marcar como leídas las notificaciones que se están viendo
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True, read_at=timezone.now())
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'guards/notifications.html', context)
