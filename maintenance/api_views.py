"""
API views específicas para notificaciones de mantenimiento
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.models import Notification
from .models import MaintenanceReport
import json


@login_required
@require_http_methods(["GET"])
def get_maintenance_notifications(request):
    """
    API endpoint para obtener notificaciones de mantenimiento en tiempo real
    """
    user = request.user
    
    # Solo para administradores
    if not (user.is_superuser or (hasattr(user, 'user_role') and user.user_role.role == 'admin')):
        return JsonResponse({
            'success': False,
            'message': 'Sin permisos para ver notificaciones de mantenimiento'
        }, status=403)
    
    try:
        # Obtener parámetros
        since = request.GET.get('since')
        limit = int(request.GET.get('limit', 10))
        
        # Filtrar notificaciones de mantenimiento
        notifications_query = Notification.objects.filter(
            recipient=user,
            notification_type='maintenance_request'
        ).order_by('-created_at')
        
        # Si se especifica 'since', obtener solo las nuevas
        new_notifications = []
        if since:
            try:
                since_timestamp = int(since) / 1000  # Convertir de milisegundos
                since_datetime = timezone.datetime.fromtimestamp(since_timestamp, tz=timezone.get_current_timezone())
                new_notifications_query = notifications_query.filter(created_at__gt=since_datetime)
                new_notifications = list(new_notifications_query.values(
                    'id', 'title', 'message', 'notification_type', 'priority', 
                    'is_read', 'created_at', 'action_url'
                ))
            except (ValueError, TypeError):
                pass
        
        # Obtener todas las notificaciones (limitadas)
        notifications = list(notifications_query[:limit].values(
            'id', 'title', 'message', 'notification_type', 'priority',
            'is_read', 'created_at', 'action_url'
        ))
        
        # Contar no leídas
        unread_count = notifications_query.filter(is_read=False).count()
        
        # Obtener estadísticas de reportes
        pending_reports = MaintenanceReport.objects.filter(status='pendiente').count()
        urgent_reports = MaintenanceReport.objects.filter(
            status='pendiente',
            priority__in=['alta', 'critica']
        ).count()
        
        return JsonResponse({
            'success': True,
            'notifications': notifications,
            'new_notifications': new_notifications,
            'unread_count': unread_count,
            'pending_reports': pending_reports,
            'urgent_reports': urgent_reports,
            'timestamp': timezone.now().timestamp() * 1000  # En milisegundos
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error obteniendo notificaciones: {str(e)}'
        }, status=500)


@login_required 
@require_http_methods(["POST"])
def create_maintenance_notification(request):
    """
    API endpoint para crear notificaciones de mantenimiento
    (llamado automáticamente cuando se crean reportes)
    """
    user = request.user
    
    try:
        data = json.loads(request.body)
        report_id = data.get('report_id')
        
        if not report_id:
            return JsonResponse({
                'success': False,
                'message': 'report_id es requerido'
            }, status=400)
        
        # Obtener el reporte
        try:
            report = MaintenanceReport.objects.get(id=report_id)
        except MaintenanceReport.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Reporte no encontrado'
            }, status=404)
        
        # Crear notificaciones para administradores
        from maintenance.views import notify_admins_new_report
        notifications_created = notify_admins_new_report(report)
        
        return JsonResponse({
            'success': True,
            'message': f'Notificaciones enviadas exitosamente',
            'notifications_created': notifications_created
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creando notificaciones: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_maintenance_stats(request):
    """
    API endpoint para obtener estadísticas de mantenimiento para badges
    """
    user = request.user
    
    # Solo para administradores
    if not (user.is_superuser or (hasattr(user, 'user_role') and user.user_role.role == 'admin')):
        return JsonResponse({
            'success': False,
            'message': 'Sin permisos'
        }, status=403)
    
    try:
        # Estadísticas de reportes
        total_reports = MaintenanceReport.objects.count()
        pending_reports = MaintenanceReport.objects.filter(status='pendiente').count()
        urgent_reports = MaintenanceReport.objects.filter(
            status='pendiente',
            priority__in=[1, 2]  # Crítica y Alta
        ).count()
        in_progress_reports = MaintenanceReport.objects.filter(status='en_proceso').count()
        
        # Notificaciones no leídas
        unread_notifications = Notification.objects.filter(
            recipient=user,
            is_read=False,
            notification_type='maintenance_request'
        ).count()
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_reports': total_reports,
                'pending_reports': pending_reports,
                'urgent_reports': urgent_reports,
                'in_progress_reports': in_progress_reports,
                'unread_notifications': unread_notifications
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error obteniendo estadísticas: {str(e)}'
        }, status=500)
