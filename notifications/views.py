from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.shortcuts import get_object_or_404
import json
import logging

from .services import push_service
from .models import PushNotification, NotificationPreferences

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class PushSubscribeView(View):
    """Vista para suscribirse a notificaciones push"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            subscription_data = data.get('subscription')
            
            if not subscription_data:
                return JsonResponse({'error': 'Datos de suscripción requeridos'}, status=400)
            
            # Suscribir usuario
            subscription = push_service.subscribe_user(request.user, subscription_data)
            
            return JsonResponse({
                'success': True,
                'message': 'Suscripción exitosa a notificaciones push',
                'subscription_id': subscription.id
            })
            
        except Exception as e:
            logger.error(f"Error en suscripción push: {str(e)}")
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class PushUnsubscribeView(View):
    """Vista para desuscribirse de notificaciones push"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            endpoint = data.get('endpoint')
            
            success = push_service.unsubscribe_user(request.user, endpoint)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': 'Desuscripción exitosa'
                })
            else:
                return JsonResponse({'error': 'Error al desuscribir'}, status=400)
            
        except Exception as e:
            logger.error(f"Error en desuscripción push: {str(e)}")
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)

@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """Obtiene las notificaciones del usuario"""
    try:
        limit = int(request.GET.get('limit', 20))
        unread_only = request.GET.get('unread_only', 'false').lower() == 'true'
        
        notifications = push_service.get_user_notifications(
            request.user, 
            limit=limit, 
            unread_only=unread_only
        )
        
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'created_at': notification.created_at.isoformat(),
                'read_at': notification.read_at.isoformat() if notification.read_at else None,
                'data': notification.data
            })
        
        unread_count = push_service.get_unread_count(request.user)
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'unread_count': unread_count
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo notificaciones: {str(e)}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def mark_notification_read(request, notification_id):
    """Marca una notificación como leída"""
    try:
        success = push_service.mark_notification_as_read(notification_id, request.user)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Notificación marcada como leída'
            })
        else:
            return JsonResponse({'error': 'Notificación no encontrada'}, status=404)
            
    except Exception as e:
        logger.error(f"Error marcando notificación como leída: {str(e)}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)

@login_required
@require_http_methods(["GET"])
def get_unread_count(request):
    """Obtiene el número de notificaciones no leídas"""
    try:
        count = push_service.get_unread_count(request.user)
        
        return JsonResponse({
            'success': True,
            'unread_count': count
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo contador no leídas: {str(e)}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class NotificationPreferencesView(View):
    """Vista para gestionar preferencias de notificaciones"""
    
    def get(self, request):
        """Obtiene las preferencias actuales del usuario"""
        try:
            preferences, created = NotificationPreferences.objects.get_or_create(
                user=request.user
            )
            
            return JsonResponse({
                'success': True,
                'preferences': {
                    'visit_notifications': preferences.visit_notifications,
                    'maintenance_notifications': preferences.maintenance_notifications,
                    'emergency_notifications': preferences.emergency_notifications,
                    'general_notifications': preferences.general_notifications,
                    'quiet_hours_enabled': preferences.quiet_hours_enabled,
                    'quiet_hours_start': preferences.quiet_hours_start.strftime('%H:%M'),
                    'quiet_hours_end': preferences.quiet_hours_end.strftime('%H:%M'),
                }
            })
            
        except Exception as e:
            logger.error(f"Error obteniendo preferencias: {str(e)}")
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)
    
    def post(self, request):
        """Actualiza las preferencias del usuario"""
        try:
            data = json.loads(request.body)
            
            preferences, created = NotificationPreferences.objects.get_or_create(
                user=request.user
            )
            
            # Actualizar preferencias
            if 'visit_notifications' in data:
                preferences.visit_notifications = data['visit_notifications']
            if 'maintenance_notifications' in data:
                preferences.maintenance_notifications = data['maintenance_notifications']
            if 'emergency_notifications' in data:
                preferences.emergency_notifications = data['emergency_notifications']
            if 'general_notifications' in data:
                preferences.general_notifications = data['general_notifications']
            if 'quiet_hours_enabled' in data:
                preferences.quiet_hours_enabled = data['quiet_hours_enabled']
            if 'quiet_hours_start' in data:
                preferences.quiet_hours_start = data['quiet_hours_start']
            if 'quiet_hours_end' in data:
                preferences.quiet_hours_end = data['quiet_hours_end']
            
            preferences.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Preferencias actualizadas exitosamente'
            })
            
        except Exception as e:
            logger.error(f"Error actualizando preferencias: {str(e)}")
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)

# Vistas para testing (solo en desarrollo)
@login_required
@require_http_methods(["POST"])
@csrf_exempt
def test_notification(request):
    """Vista para probar notificaciones (solo desarrollo)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        data = json.loads(request.body)
        notification_type = data.get('type', 'general_announcement')
        
        context = {
            'message': data.get('message', 'Notificación de prueba'),
            'timestamp': '15:30',
            'date': '24/07/2025'
        }
        
        notifications = push_service.send_notification_to_user(
            request.user,
            notification_type,
            context
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Notificación de prueba enviada',
            'notifications_sent': len(notifications)
        })
        
    except Exception as e:
        logger.error(f"Error en notificación de prueba: {str(e)}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)

@login_required  
@require_http_methods(["POST"])
@csrf_exempt
def send_emergency_alert(request):
    """Vista para enviar alertas de emergencia"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        data = json.loads(request.body)
        message = data.get('message', 'Alerta de emergencia')
        target_roles = data.get('target_roles', ['admin', 'guard'])
        
        notifications = push_service.send_emergency_alert(message, target_roles)
        
        return JsonResponse({
            'success': True,
            'message': 'Alerta de emergencia enviada',
            'notifications_sent': len(notifications)
        })
        
    except Exception as e:
        logger.error(f"Error enviando alerta de emergencia: {str(e)}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)
