from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
import json
from .models import Notification


@login_required
@require_http_methods(["GET"])
def notifications_api(request):
    """API para obtener notificaciones del usuario"""
    try:
        user = request.user
        
        # Parámetros de consulta
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        only_unread = request.GET.get('only_unread', 'false').lower() == 'true'
        notification_type = request.GET.get('type')
        priority = request.GET.get('priority')
        
        # Construir queryset
        queryset = Notification.objects.filter(recipient=user)
        
        if only_unread:
            queryset = queryset.filter(is_read=False)
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        if priority:
            queryset = queryset.filter(priority=int(priority))
        
        # Ordenar por prioridad y fecha
        queryset = queryset.order_by('priority', '-created_at')
        
        # Paginación
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        # Serializar notificaciones
        notifications = []
        for notification in page_obj:
            notifications.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'priority': notification.priority,
                'priority_display': notification.priority_display,
                'priority_color': notification.priority_color,
                'status': notification.status,
                'is_read': notification.is_read,
                'is_urgent': notification.is_urgent,
                'requires_action': notification.requires_action,
                'action_url': notification.action_url,
                'action_text': notification.action_text,
                'icon': notification.icon,
                'color': notification.color,
                'emoji_icon': notification.emoji_icon,
                'sender_name': notification.sender.get_full_name() if notification.sender else 'Sistema',
                'created_at': notification.created_at.isoformat(),
                'read_at': notification.read_at.isoformat() if notification.read_at else None,
                'age_in_hours': notification.age_in_hours,
                'thread_key': notification.thread_key,
                'has_replies': notification.replies.exists(),
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notifications,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            },
            'counts': {
                'total': user.notifications.count(),
                'unread': user.notifications.filter(is_read=False).count(),
                'urgent': user.notifications.filter(priority__in=[1, 2], is_read=False).count(),
                'today': user.notifications.filter(
                    created_at__date=timezone.now().date()
                ).count(),
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def mark_notification_read(request, notification_id):
    """Marcar una notificación como leída"""
    try:
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            recipient=request.user
        )
        
        notification.mark_as_read()
        
        return JsonResponse({
            'success': True,
            'message': 'Notificación marcada como leída',
            'notification': {
                'id': notification.id,
                'is_read': notification.is_read,
                'read_at': notification.read_at.isoformat() if notification.read_at else None,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def mark_all_notifications_read(request):
    """Marcar todas las notificaciones como leídas"""
    try:
        unread_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        )
        
        count = unread_notifications.count()
        
        unread_notifications.update(
            is_read=True,
            read_at=timezone.now(),
            status='read'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{count} notificaciones marcadas como leídas',
            'marked_count': count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def dismiss_notification(request, notification_id):
    """Descartar una notificación"""
    try:
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            recipient=request.user
        )
        
        notification.dismiss()
        
        return JsonResponse({
            'success': True,
            'message': 'Notificación descartada',
            'notification': {
                'id': notification.id,
                'is_dismissed': notification.is_dismissed,
                'status': notification.status,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def notification_counts(request):
    """Obtener contadores rápidos de notificaciones"""
    try:
        user = request.user
        
        # Contadores principales
        total = user.notifications.count()
        unread = user.notifications.filter(is_read=False).count()
        urgent = user.notifications.filter(
            priority__in=[1, 2], 
            is_read=False
        ).count()
        
        # Contadores por tipo
        type_counts = {}
        type_queryset = user.notifications.filter(is_read=False).values(
            'notification_type'
        ).annotate(count=Count('id'))
        
        for item in type_queryset:
            type_counts[item['notification_type']] = item['count']
        
        return JsonResponse({
            'success': True,
            'counts': {
                'total': total,
                'unread': unread,
                'urgent': urgent,
                'by_type': type_counts,
                'has_urgent': urgent > 0,
                'has_unread': unread > 0,
            },
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def recent_notifications(request):
    """Obtener las notificaciones más recientes para el header"""
    try:
        user = request.user
        limit = int(request.GET.get('limit', 5))
        
        # Obtener las más recientes no leídas primero, luego las leídas
        recent = list(user.notifications.filter(is_read=False).order_by('priority', '-created_at')[:limit])
        
        if len(recent) < limit:
            remaining = limit - len(recent)
            read_recent = list(user.notifications.filter(is_read=True).order_by('-created_at')[:remaining])
            recent.extend(read_recent)
        
        notifications = []
        for notification in recent:
            notifications.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message[:100] + '...' if len(notification.message) > 100 else notification.message,
                'type': notification.notification_type,
                'priority': notification.priority,
                'priority_color': notification.priority_color,
                'is_read': notification.is_read,
                'is_urgent': notification.is_urgent,
                'emoji_icon': notification.emoji_icon,
                'action_url': notification.action_url,
                'created_at': notification.created_at.isoformat(),
                'age_in_hours': notification.age_in_hours,
                'time_ago': get_time_ago(notification.created_at),
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notifications,
            'counts': {
                'unread': user.notifications.filter(is_read=False).count(),
                'urgent': user.notifications.filter(priority__in=[1, 2], is_read=False).count(),
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def get_time_ago(datetime_obj):
    """Obtener representación de tiempo transcurrido"""
    now = timezone.now()
    diff = now - datetime_obj
    
    if diff.days > 0:
        return f"hace {diff.days} día{'s' if diff.days != 1 else ''}"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"hace {hours} hora{'s' if hours != 1 else ''}"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"hace {minutes} minuto{'s' if minutes != 1 else ''}"
    else:
        return "hace un momento"


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def send_test_notification(request):
    """Enviar notificación de prueba (solo para administradores)"""
    try:
        if not (request.user.is_superuser or 
                (hasattr(request.user, 'user_role') and request.user.user_role.role == 'admin')):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para esta acción'
            }, status=403)
        
        data = json.loads(request.body) if request.body else {}
        
        notification = Notification.objects.create(
            recipient=request.user,
            sender=request.user,
            title=data.get('title', '🧪 Notificación de Prueba'),
            message=data.get('message', 'Esta es una notificación de prueba para validar el sistema.'),
            notification_type=data.get('type', 'general'),
            priority=int(data.get('priority', 3)),
            icon=data.get('icon', 'fas fa-flask'),
            color=data.get('color', 'blue'),
            requires_action=data.get('requires_action', False),
            action_text=data.get('action_text'),
            action_url=data.get('action_url'),
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Notificación de prueba enviada',
            'notification': {
                'id': notification.id,
                'title': notification.title,
                'created_at': notification.created_at.isoformat(),
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
