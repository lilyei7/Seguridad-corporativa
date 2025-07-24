from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
from .models import Notification

@login_required
@require_http_methods(["GET"])
def get_notifications_api(request):
    """API para obtener notificaciones del usuario actual"""
    try:
        notifications = Notification.objects.filter(
            recipient=request.user
        ).select_related(
            'maintenance_report', 'maintenance_report__area'
        ).order_by('-created_at')[:20]  # Últimas 20 notificaciones
        
        notifications_data = []
        for notification in notifications:
            # Crear URL de acción si es de mantenimiento
            action_url = None
            if notification.maintenance_report:
                action_url = f"/maintenance/reports/{notification.maintenance_report.id}/"
            
            # Determinar el ícono según el tipo
            icon = 'fas fa-wrench'  # Por defecto para mantenimiento
            if notification.notification_type == 'maintenance_update':
                icon = 'fas fa-sync-alt'
            elif notification.notification_type == 'visit':
                icon = 'fas fa-user-friends'
            elif notification.notification_type == 'system':
                icon = 'fas fa-cog'
            
            # Calcular tiempo relativo
            now = timezone.now()
            time_diff = now - notification.created_at
            
            if time_diff < timedelta(minutes=1):
                time_ago = "Ahora"
            elif time_diff < timedelta(hours=1):
                minutes = int(time_diff.total_seconds() / 60)
                time_ago = f"Hace {minutes}m"
            elif time_diff < timedelta(days=1):
                hours = int(time_diff.total_seconds() / 3600)
                time_ago = f"Hace {hours}h"
            else:
                days = time_diff.days
                time_ago = f"Hace {days}d"
            
            notifications_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'is_read': notification.is_read,
                'priority': notification.priority,
                'created_at': notification.created_at.isoformat(),
                'time_ago': time_ago,
                'action_url': action_url,
                'icon': icon,
                'notification_type': notification.notification_type,
            })
        
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        return JsonResponse({
            'notifications': notifications_data,
            'unread_count': unread_count,
            'success': True
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)

@login_required
@require_http_methods(["POST"])
def mark_notification_read_api(request, notification_id):
    """API para marcar una notificación como leída"""
    try:
        notification = Notification.objects.get(
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
        
    except Notification.DoesNotExist:
        return JsonResponse({
            'error': 'Notificación no encontrada',
            'success': False
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)

@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read_api(request):
    """API para marcar todas las notificaciones como leídas"""
    try:
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{count} notificaciones marcadas como leídas',
            'count': count
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)
