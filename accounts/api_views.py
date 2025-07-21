from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from .models import Notification
from .decorators import admin_required
import json

@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """API endpoint para obtener notificaciones del usuario actual"""
    user = request.user
    
    # Solo los admins pueden ver todas las notificaciones
    if hasattr(user, 'user_role') and user.user_role.role == 'admin':
        notifications = Notification.objects.filter(
            recipient=user
        ).order_by('-created_at')
    else:
        # Otros usuarios solo ven sus notificaciones específicas
        notifications = Notification.objects.filter(
            recipient=user,
            is_dismissed=False
        ).order_by('-created_at')
    
    # Paginación
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 20)
    
    paginator = Paginator(notifications, per_page)
    page_obj = paginator.get_page(page)
    
    # Contar no leídas
    unread_count = notifications.filter(is_read=False).count()
    
    # Serializar notificaciones
    notifications_data = []
    for notification in page_obj:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'notification_type': notification.notification_type,
            'priority': notification.priority,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'url': notification.url,
            'icon': get_notification_icon(notification.notification_type),
            'color': get_notification_color(notification.priority)
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_count': paginator.count
    })

@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Marcar una notificación específica como leída"""
    try:
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            recipient=request.user
        )
        
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notificación marcada como leída'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    """Marcar todas las notificaciones del usuario como leídas"""
    try:
        user = request.user
        
        # Actualizar todas las notificaciones no leídas
        updated_count = Notification.objects.filter(
            recipient=user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{updated_count} notificaciones marcadas como leídas',
            'updated_count': updated_count
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_http_methods(["DELETE"])
def delete_notification(request, notification_id):
    """Eliminar una notificación específica"""
    try:
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            recipient=request.user
        )
        
        notification.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Notificación eliminada correctamente'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
def notifications_page(request):
    """Vista de página completa de notificaciones"""
    user = request.user
    
    # Obtener notificaciones del usuario
    if hasattr(user, 'user_role') and user.user_role.role == 'admin':
        notifications = Notification.objects.filter(
            recipient=user
        ).order_by('-created_at')
    else:
        notifications = Notification.objects.filter(
            recipient=user,
            is_dismissed=False
        ).order_by('-created_at')
    
    # Filtros
    notification_type = request.GET.get('type')
    is_read = request.GET.get('read')
    priority = request.GET.get('priority')
    
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    if is_read is not None:
        is_read_bool = is_read.lower() == 'true'
        notifications = notifications.filter(is_read=is_read_bool)
    
    if priority:
        notifications = notifications.filter(priority=priority)
    
    # Paginación
    paginator = Paginator(notifications, 15)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    # Estadísticas
    total_notifications = notifications.count()
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': page_obj,
        'total_notifications': total_notifications,
        'unread_count': unread_count,
        'current_type': notification_type,
        'current_read': is_read,
        'current_priority': priority,
        'notification_types': Notification.NOTIFICATION_TYPES,
        'priority_choices': Notification.PRIORITY_CHOICES,
    }
    
    return render(request, 'accounts/notifications.html', context)

@admin_required
@require_http_methods(["POST"])
def send_bulk_notification(request):
    """Enviar notificación masiva (solo para admins)"""
    try:
        data = json.loads(request.body)
        
        title = data.get('title')
        message = data.get('message')
        notification_type = data.get('type', 'general')
        priority = data.get('priority', 'medium')
        recipient_roles = data.get('recipient_roles', [])
        
        if not title or not message:
            return JsonResponse({
                'success': False,
                'message': 'Título y mensaje son requeridos'
            }, status=400)
        
        # Obtener usuarios según roles
        from accounts.models import UserRole
        
        if recipient_roles:
            user_roles = UserRole.objects.filter(role__in=recipient_roles)
            recipients = [ur.user for ur in user_roles]
        else:
            # Enviar a todos los usuarios
            from django.contrib.auth.models import User
            recipients = User.objects.filter(is_active=True)
        
        # Crear notificaciones
        notifications_created = 0
        for recipient in recipients:
            Notification.objects.create(
                recipient=recipient,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                sender=request.user
            )
            notifications_created += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Se enviaron {notifications_created} notificaciones',
            'notifications_sent': notifications_created
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_http_methods(["GET"])
def get_notification_stats(request):
    """Obtener estadísticas de notificaciones para el dashboard del admin"""
    user = request.user
    
    if not (hasattr(user, 'user_role') and user.user_role.role == 'admin'):
        return JsonResponse({
            'success': False,
            'message': 'Sin permisos para ver estadísticas'
        }, status=403)
    
    # Estadísticas generales
    total_notifications = Notification.objects.count()
    unread_notifications = Notification.objects.filter(is_read=False).count()
    
    # Notificaciones por tipo
    notifications_by_type = {}
    for choice in Notification.NOTIFICATION_TYPES:
        count = Notification.objects.filter(notification_type=choice[0]).count()
        notifications_by_type[choice[1]] = count
    
    # Notificaciones por prioridad
    notifications_by_priority = {}
    for choice in Notification.PRIORITY_CHOICES:
        count = Notification.objects.filter(priority=choice[0]).count()
        notifications_by_priority[choice[1]] = count
    
    # Notificaciones recientes (últimas 24 horas)
    from datetime import timedelta
    yesterday = timezone.now() - timedelta(days=1)
    recent_notifications = Notification.objects.filter(
        created_at__gte=yesterday
    ).count()
    
    return JsonResponse({
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'recent_notifications': recent_notifications,
        'notifications_by_type': notifications_by_type,
        'notifications_by_priority': notifications_by_priority
    })

def get_notification_icon(notification_type):
    """Obtener icono según el tipo de notificación"""
    icons = {
        'maintenance_request': 'fas fa-tools',
        'incident_report': 'fas fa-exclamation-triangle',
        'visit_notification': 'fas fa-user-friends',
        'system_alert': 'fas fa-cog',
        'general': 'fas fa-bell'
    }
    return icons.get(notification_type, 'fas fa-bell')

def get_notification_color(priority):
    """Obtener color según la prioridad"""
    colors = {
        'urgent': '#ef4444',
        'high': '#f97316',
        'medium': '#3b82f6',
        'low': '#10b981'
    }
    return colors.get(priority, '#3b82f6')
