from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from accounts.decorators import tenant_required, role_required
from accounts.models import Notification
from visits.models import Visit, VisitRequest
from maintenance.models import MaintenanceRequest
from tenants.models import Tenant
from django.db.models import Q, Count


@tenant_required
def tenant_dashboard(request):
    """Dashboard específico para inquilinos"""
    context = {}
    
    try:
        # Obtener perfil del inquilino
        if hasattr(request.user, 'role_profile') and request.user.role_profile.tenant_profile:
            tenant = request.user.role_profile.tenant_profile
            context['tenant'] = tenant
            
            # Estadísticas del inquilino
            context['stats'] = {
                'total_visits': Visit.objects.filter(tenant=tenant).count(),
                'pending_visits': Visit.objects.filter(
                    tenant=tenant, 
                    status='pendiente'
                ).count(),
                'maintenance_requests': MaintenanceRequest.objects.filter(
                    created_by=request.user
                ).count(),
                'unread_notifications': request.user.notifications.filter(
                    is_read=False
                ).count(),
            }
            
            # Visitas recientes
            context['recent_visits'] = Visit.objects.filter(
                tenant=tenant
            ).order_by('-created_at')[:5]
            
            # Solicitudes de mantenimiento recientes
            context['recent_maintenance'] = MaintenanceRequest.objects.filter(
                created_by=request.user
            ).order_by('-created_at')[:5]
            
            # Notificaciones recientes
            context['recent_notifications'] = request.user.notifications.filter(
                is_read=False
            ).order_by('-created_at')[:5]
            
        else:
            messages.error(request, "No tienes un perfil de inquilino asociado. Contacta al administrador.")
            return redirect('dashboard:index')
    
    except Exception as e:
        messages.error(request, f"Error al cargar el dashboard: {str(e)}")
        return redirect('dashboard:index')
    
    return render(request, 'tenants/dashboard.html', context)


@tenant_required
def tenant_visits(request):
    """Vista de visitas para inquilinos - solo pueden ver las suyas"""
    tenant = request.user.role_profile.tenant_profile
    
    visits = Visit.objects.filter(tenant=tenant).order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        visits = visits.filter(status=status_filter)
    
    context = {
        'visits': visits,
        'tenant': tenant,
        'status_choices': Visit.STATUS_CHOICES,
        'can_create_visits': True,
    }
    
    return render(request, 'tenants/visits.html', context)


@tenant_required
def create_tenant_visit(request):
    """Crear nueva visita como inquilino"""
    tenant = request.user.role_profile.tenant_profile
    
    if request.method == 'POST':
        try:
            visit = Visit.objects.create(
                tenant=tenant,
                visitor_name=request.POST.get('visitor_name'),
                visitor_email=request.POST.get('visitor_email', ''),
                visitor_phone=request.POST.get('visitor_phone', ''),
                visitor_company=request.POST.get('visitor_company', ''),
                visit_purpose=request.POST.get('visit_purpose'),
                scheduled_date=request.POST.get('scheduled_date'),
                scheduled_time=request.POST.get('scheduled_time'),
                duration_hours=request.POST.get('duration_hours', 1),
                notes=request.POST.get('notes', ''),
                created_by=request.user,
                status='pendiente'
            )
            
            # Notificar a administradores
            Notification.objects.create(
                recipient_id=1,  # Asumiendo que el admin tiene ID 1
                sender=request.user,
                title=f"Nueva visita programada: {visit.visitor_name}",
                message=f"El inquilino {tenant.tenant_name} ha programado una visita para {visit.visitor_name} el {visit.scheduled_date}.",
                notification_type='visit_notification',
                priority='medium'
            )
            
            messages.success(request, "Visita creada exitosamente.")
            return redirect('tenants:visits')
            
        except Exception as e:
            messages.error(request, f"Error al crear la visita: {str(e)}")
    
    context = {
        'tenant': tenant,
    }
    
    return render(request, 'tenants/create_visit.html', context)


@tenant_required
def tenant_maintenance_requests(request):
    """Vista de solicitudes de mantenimiento para inquilinos"""
    requests = MaintenanceRequest.objects.filter(
        created_by=request.user
    ).order_by('-created_at')
    
    context = {
        'maintenance_requests': requests,
        'can_create_requests': True,
    }
    
    return render(request, 'tenants/maintenance_requests.html', context)


@tenant_required
def create_maintenance_request(request):
    """Crear nueva solicitud de mantenimiento"""
    tenant = request.user.role_profile.tenant_profile
    
    if request.method == 'POST':
        try:
            maintenance_request = MaintenanceRequest.objects.create(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                category=request.POST.get('category'),
                priority=request.POST.get('priority', 'medium'),
                location=f"Piso {tenant.piso}, Oficina {tenant.numero_oficina}",
                created_by=request.user,
                status='pendiente'
            )
            
            # Notificar a administradores
            Notification.send_maintenance_request(
                sender=request.user,
                title=maintenance_request.title,
                message=f"Solicitud de mantenimiento de {tenant.tenant_name}: {maintenance_request.description}"
            )
            
            messages.success(request, "Solicitud de mantenimiento enviada exitosamente.")
            return redirect('tenants:maintenance_requests')
            
        except Exception as e:
            messages.error(request, f"Error al crear la solicitud: {str(e)}")
    
    context = {
        'tenant': tenant,
        'categories': MaintenanceRequest.CATEGORY_CHOICES,
        'priorities': MaintenanceRequest.PRIORITY_CHOICES,
    }
    
    return render(request, 'tenants/create_maintenance_request.html', context)


@tenant_required
def tenant_employees(request):
    """Gestión de empleados del inquilino"""
    tenant = request.user.role_profile.tenant_profile
    
    # Aquí podrías tener un modelo de empleados por inquilino
    # Por ahora, mostraremos una vista básica
    
    context = {
        'tenant': tenant,
    }
    
    return render(request, 'tenants/employees.html', context)


@tenant_required
def tenant_notifications(request):
    """Ver notificaciones del inquilino"""
    notifications = request.user.notifications.order_by('-created_at')
    
    # Marcar como leídas las notificaciones que se están viendo
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True, read_at=timezone.now())
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'tenants/notifications.html', context)


@tenant_required
def mark_notification_read(request, notification_id):
    """Marcar notificación como leída via AJAX"""
    if request.method == 'POST':
        try:
            notification = get_object_or_404(
                Notification, 
                id=notification_id, 
                recipient=request.user
            )
            notification.mark_as_read()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
