import json
import logging
from typing import List, Dict, Any, Optional
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import PushSubscription, PushNotification, NotificationTemplate, NotificationPreferences

# Para implementación futura con pywebpush
# from pywebpush import webpush, WebPushException

User = get_user_model()
logger = logging.getLogger(__name__)

class PushNotificationService:
    """Servicio para manejo de notificaciones push"""
    
    def __init__(self):
        # Configuración VAPID (se configurará en settings)
        self.vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', None)
        self.vapid_public_key = getattr(settings, 'VAPID_PUBLIC_KEY', None)
        self.vapid_email = getattr(settings, 'VAPID_EMAIL', 'admin@securecorp.com')
    
    def subscribe_user(self, user: User, subscription_data: Dict[str, Any]) -> PushSubscription:
        """Suscribe a un usuario a las notificaciones push"""
        try:
            subscription, created = PushSubscription.objects.update_or_create(
                user=user,
                endpoint=subscription_data['endpoint'],
                defaults={
                    'p256dh_key': subscription_data['keys']['p256dh'],
                    'auth_key': subscription_data['keys']['auth'],
                    'user_agent': subscription_data.get('userAgent', ''),
                    'is_active': True
                }
            )
            
            # Crear preferencias por defecto si no existen
            NotificationPreferences.objects.get_or_create(user=user)
            
            logger.info(f"Usuario {user.username} {'suscrito' if created else 'actualizado'} a push notifications")
            return subscription
        
        except Exception as e:
            logger.error(f"Error al suscribir usuario {user.username}: {str(e)}")
            raise
    
    def unsubscribe_user(self, user: User, endpoint: str = None) -> bool:
        """Desuscribe a un usuario de las notificaciones push"""
        try:
            if endpoint:
                # Desuscribir endpoint específico
                PushSubscription.objects.filter(user=user, endpoint=endpoint).update(is_active=False)
            else:
                # Desuscribir todas las suscripciones del usuario
                PushSubscription.objects.filter(user=user).update(is_active=False)
            
            logger.info(f"Usuario {user.username} desuscrito de push notifications")
            return True
        
        except Exception as e:
            logger.error(f"Error al desuscribir usuario {user.username}: {str(e)}")
            return False
    
    def send_notification_to_user(self, 
                                user: User, 
                                notification_type: str, 
                                context: Dict[str, Any],
                                visit=None,
                                maintenance_report=None) -> List[PushNotification]:
        """Envía una notificación a un usuario específico"""
        
        # Verificar preferencias del usuario
        preferences = NotificationPreferences.objects.filter(user=user).first()
        if preferences and not preferences.should_send_notification(notification_type):
            logger.info(f"Notificación {notification_type} no enviada a {user.username} por preferencias")
            return []
        
        # Obtener template de notificación
        template = NotificationTemplate.objects.filter(
            notification_type=notification_type,
            is_active=True
        ).first()
        
        if not template:
            logger.warning(f"No se encontró template para {notification_type}")
            return []
        
        # Renderizar notificación
        notification_data = template.render_notification(context)
        
        # Crear registro de notificación
        push_notification = PushNotification.objects.create(
            user=user,
            notification_type=notification_type,
            title=notification_data['title'],
            message=notification_data['body'],
            data=notification_data,
            visit=visit,
            maintenance_report=maintenance_report
        )
        
        # Obtener suscripciones activas del usuario
        subscriptions = PushSubscription.objects.filter(user=user, is_active=True)
        
        sent_notifications = []
        for subscription in subscriptions:
            try:
                # Enviar notificación push
                success = self._send_push_to_subscription(subscription, notification_data)
                
                if success:
                    push_notification.mark_as_sent()
                    sent_notifications.append(push_notification)
                    logger.info(f"Notificación enviada a {user.username}")
                else:
                    push_notification.mark_as_failed("Error al enviar push")
                    
            except Exception as e:
                push_notification.mark_as_failed(str(e))
                logger.error(f"Error enviando notificación a {user.username}: {str(e)}")
        
        return sent_notifications
    
    def send_notification_to_role(self, 
                                role: str, 
                                notification_type: str, 
                                context: Dict[str, Any]) -> List[PushNotification]:
        """Envía notificación a todos los usuarios de un rol específico"""
        
        users = self._get_users_by_role(role)
        sent_notifications = []
        
        for user in users:
            notifications = self.send_notification_to_user(
                user, notification_type, context
            )
            sent_notifications.extend(notifications)
        
        logger.info(f"Notificación {notification_type} enviada a {len(users)} usuarios del rol {role}")
        return sent_notifications
    
    def broadcast_notification(self, 
                             notification_type: str, 
                             title: str = None,
                             message: str = None,
                             context: Dict = None) -> int:
        """Envía notificación a todos los usuarios con suscripciones activas"""
        
        if context is None:
            context = {}
        
        if title:
            context['title'] = title
        if message:
            context['message'] = message
        
        # Obtener todos los usuarios con suscripciones activas
        users_with_subscriptions = User.objects.filter(
            push_subscriptions__is_active=True
        ).distinct()
        
        sent_count = 0
        for user in users_with_subscriptions:
            try:
                notifications = self.send_notification_to_user(
                    user, notification_type, context
                )
                if notifications:
                    sent_count += 1
            except Exception as e:
                logger.error(f"Error enviando notificación a {user.username}: {str(e)}")
                continue
        
        logger.info(f"Notificación broadcast {notification_type} enviada a {sent_count} usuarios")
        return sent_count
    
    def send_emergency_alert(self, 
                           message: str, 
                           target_roles: List[str] = None) -> List[PushNotification]:
        """Envía alerta de emergencia a roles específicos"""
        
        if target_roles is None:
            target_roles = ['admin', 'guard']  # Por defecto a admins y vigilantes
        
        context = {
            'message': message,
            'timestamp': timezone.now().strftime('%H:%M'),
            'date': timezone.now().strftime('%d/%m/%Y')
        }
        
        sent_notifications = []
        for role in target_roles:
            notifications = self.send_notification_to_role(
                role, 'emergency_alert', context
            )
            sent_notifications.extend(notifications)
        
        return sent_notifications
    
    def _send_push_to_subscription(self, 
                                 subscription: PushSubscription, 
                                 notification_data: Dict[str, Any]) -> bool:
        """Envía push notification a una suscripción específica"""
        
        # Por ahora simulamos el envío exitoso
        # En producción aquí iría la implementación con pywebpush
        
        # TODO: Implementar con pywebpush cuando esté disponible
        # try:
        #     webpush(
        #         subscription_info=subscription.subscription_info,
        #         data=json.dumps(notification_data),
        #         vapid_private_key=self.vapid_private_key,
        #         vapid_claims={
        #             "sub": f"mailto:{self.vapid_email}",
        #             "aud": subscription.endpoint
        #         }
        #     )
        #     return True
        # except WebPushException as e:
        #     logger.error(f"Error en webpush: {str(e)}")
        #     return False
        
        # Simulación para desarrollo
        logger.info(f"Simulando envío de push: {notification_data['title']}")
        return True
    
    def _get_users_by_role(self, role: str) -> List[User]:
        """Obtiene usuarios según su rol"""
        if role == 'admin':
            return User.objects.filter(is_staff=True)
        elif role == 'guard':
            return User.objects.filter(guard__isnull=False, guard__status='activo')
        elif role == 'tenant':
            return User.objects.filter(tenant__isnull=False, tenant__is_active=True)
        else:
            return []
    
    def get_user_notifications(self, 
                             user: User, 
                             limit: int = 20, 
                             unread_only: bool = False) -> List[PushNotification]:
        """Obtiene las notificaciones de un usuario"""
        
        queryset = PushNotification.objects.filter(user=user)
        
        if unread_only:
            queryset = queryset.filter(read_at__isnull=True)
        
        return queryset.order_by('-created_at')[:limit]
    
    def mark_notification_as_read(self, notification_id: int, user: User) -> bool:
        """Marca una notificación como leída"""
        try:
            notification = PushNotification.objects.get(id=notification_id, user=user)
            notification.mark_as_read()
            return True
        except PushNotification.DoesNotExist:
            return False
    
    def get_unread_count(self, user: User) -> int:
        """Obtiene el número de notificaciones no leídas"""
        return PushNotification.objects.filter(
            user=user, 
            read_at__isnull=True
        ).count()


# Instancia global del servicio
push_service = PushNotificationService()


# Funciones de conveniencia para casos de uso específicos

def notify_visit_approved(visit):
    """Notifica al inquilino que su visita fue aprobada"""
    context = {
        'visitor_name': visit.visitor_name,
        'date': visit.scheduled_date.strftime('%d/%m/%Y'),
        'time': visit.scheduled_time.strftime('%H:%M'),
        'unit': visit.tenant.unit_number
    }
    
    return push_service.send_notification_to_user(
        visit.tenant.user, 
        'visit_approved', 
        context,
        visit=visit
    )

def notify_visit_rejected(visit, reason=''):
    """Notifica al inquilino que su visita fue rechazada"""
    context = {
        'visitor_name': visit.visitor_name,
        'date': visit.scheduled_date.strftime('%d/%m/%Y'),
        'time': visit.scheduled_time.strftime('%H:%M'),
        'reason': reason
    }
    
    return push_service.send_notification_to_user(
        visit.tenant.user, 
        'visit_rejected', 
        context,
        visit=visit
    )

def notify_visitor_arrived(visit):
    """Notifica al inquilino que su visitante llegó"""
    context = {
        'visitor_name': visit.visitor_name,
        'time': timezone.now().strftime('%H:%M'),
        'unit': visit.tenant.unit_number
    }
    
    return push_service.send_notification_to_user(
        visit.tenant.user, 
        'visit_arrived', 
        context,
        visit=visit
    )

def notify_new_visit_request(visit):
    """Notifica a vigilantes sobre nueva solicitud de visita"""
    context = {
        'visitor_name': visit.visitor_name,
        'tenant_name': visit.tenant.user.get_full_name(),
        'unit': visit.tenant.unit_number,
        'date': visit.scheduled_date.strftime('%d/%m/%Y'),
        'time': visit.scheduled_time.strftime('%H:%M')
    }
    
    return push_service.send_notification_to_role(
        'guard', 
        'visit_request', 
        context
    )

def notify_maintenance_assigned(maintenance_report):
    """Notifica sobre asignación de mantenimiento"""
    context = {
        'title': maintenance_report.title,
        'unit': maintenance_report.tenant.unit_number if maintenance_report.tenant else 'N/A',
        'priority': maintenance_report.get_priority_display(),
        'date': maintenance_report.created_at.strftime('%d/%m/%Y')
    }
    
    return push_service.send_notification_to_user(
        maintenance_report.tenant.user, 
        'maintenance_assigned', 
        context,
        maintenance_report=maintenance_report
    )

def send_emergency_broadcast(message, target_roles=['admin', 'guard']):
    """Envía alerta de emergencia masiva"""
    return push_service.send_emergency_alert(message, target_roles)
