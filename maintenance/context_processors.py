from django.db.models import Q
from accounts.models import Notification


def maintenance_notifications(request):
    """
    Context processor para proporcionar información de notificaciones
    de mantenimiento en todas las plantillas
    """
    context = {
        'maintenance_notifications_count': 0,
        'urgent_maintenance_reports': 0,
        'pending_maintenance_reports': 0,
    }
    
    if request.user.is_authenticated:
        # Solo para administradores
        if (request.user.is_superuser or 
            (hasattr(request.user, 'user_role') and request.user.user_role.role == 'admin')):
            
            try:
                # Contar notificaciones no leídas relacionadas con mantenimiento
                maintenance_notifications = Notification.objects.filter(
                    recipient=request.user,
                    is_read=False,
                    notification_type='maintenance_request'
                ).count()
                
                context['maintenance_notifications_count'] = maintenance_notifications
                
                # Contar reportes pendientes y urgentes
                from .models import MaintenanceReport
                
                pending_reports = MaintenanceReport.objects.filter(
                    status='pendiente'
                ).count()
                
                urgent_reports = MaintenanceReport.objects.filter(
                    status='pendiente',
                    priority__in=[1, 2]  # Crítica y Alta
                ).count()
                
                context['pending_maintenance_reports'] = pending_reports
                context['urgent_maintenance_reports'] = urgent_reports
                
            except Exception as e:
                # En caso de error, usar valores por defecto
                pass
    
    return context
