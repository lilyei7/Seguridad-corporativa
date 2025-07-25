from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()

class PushSubscription(models.Model):
    """Modelo para almacenar suscripciones push de usuarios"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario',
        related_name='push_subscriptions'
    )
    endpoint = models.URLField(max_length=500)
    p256dh_key = models.CharField(max_length=255, verbose_name="Clave P256DH")
    auth_key = models.CharField(max_length=255, verbose_name="Clave Auth")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Suscripción Push"
        verbose_name_plural = "Suscripciones Push"
        unique_together = ['user', 'endpoint']
    
    def __str__(self):
        return f"{self.user.username} - {self.endpoint[:50]}..."
    
    @property
    def subscription_info(self):
        """Retorna la información de suscripción en formato para pywebpush"""
        return {
            "endpoint": self.endpoint,
            "keys": {
                "p256dh": self.p256dh_key,
                "auth": self.auth_key
            }
        }

class NotificationTemplate(models.Model):
    """Templates para diferentes tipos de notificaciones"""
    NOTIFICATION_TYPES = [
        ('visit_approved', 'Visita Aprobada'),
        ('visit_rejected', 'Visita Rechazada'),
        ('visit_arrived', 'Visitante Llegó'),
        ('visit_reminder', 'Recordatorio de Visita'),
        ('maintenance_assigned', 'Mantenimiento Asignado'),
        ('maintenance_completed', 'Mantenimiento Completado'),
        ('emergency_alert', 'Alerta de Emergencia'),
        ('general_announcement', 'Anuncio General'),
    ]
    
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, unique=True)
    title_template = models.CharField(max_length=200, verbose_name="Plantilla del Título")
    body_template = models.TextField(verbose_name="Plantilla del Mensaje")
    icon_url = models.URLField(blank=True, verbose_name="URL del Icono")
    action_url = models.CharField(max_length=200, blank=True, verbose_name="URL de Acción")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Plantilla de Notificación"
        verbose_name_plural = "Plantillas de Notificaciones"
    
    def __str__(self):
        return f"{self.get_notification_type_display()}"
    
    def render_notification(self, context):
        """Renderiza la notificación con el contexto dado"""
        title = self.title_template.format(**context)
        body = self.body_template.format(**context)
        
        notification_data = {
            'title': title,
            'body': body,
            'icon': self.icon_url or '/static/img/icon-192x192.png',
            'badge': '/static/img/badge-72x72.png',
            'tag': self.notification_type,
            'requireInteraction': self.notification_type in ['emergency_alert'],
            'actions': []
        }
        
        if self.action_url:
            notification_data['data'] = {'url': self.action_url.format(**context)}
            notification_data['actions'] = [
                {'action': 'view', 'title': 'Ver', 'icon': '/static/img/view-icon.png'},
                {'action': 'dismiss', 'title': 'Cerrar'}
            ]
        
        return notification_data

class PushNotification(models.Model):
    """Registro de notificaciones enviadas"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('sent', 'Enviada'),
        ('failed', 'Fallida'),
        ('delivered', 'Entregada'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_notifications_sent')
    notification_type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True, verbose_name="Datos adicionales")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Relacionar con modelos específicos
    visit = models.ForeignKey('visits.Visit', on_delete=models.CASCADE, null=True, blank=True)
    maintenance_report = models.ForeignKey('maintenance.MaintenanceReport', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = "Notificación Push"
        verbose_name_plural = "Notificaciones Push"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.status})"
    
    def mark_as_read(self):
        """Marca la notificación como leída"""
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])
    
    def mark_as_sent(self):
        """Marca la notificación como enviada"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])
    
    def mark_as_failed(self, error_message):
        """Marca la notificación como fallida"""
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message'])

class NotificationPreferences(models.Model):
    """Preferencias de notificaciones del usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Preferencias por tipo de notificación
    visit_notifications = models.BooleanField(default=True, verbose_name="Notificaciones de Visitas")
    maintenance_notifications = models.BooleanField(default=True, verbose_name="Notificaciones de Mantenimiento")
    emergency_notifications = models.BooleanField(default=True, verbose_name="Alertas de Emergencia")
    general_notifications = models.BooleanField(default=True, verbose_name="Anuncios Generales")
    
    # Configuraciones de tiempo
    quiet_hours_start = models.TimeField(default="22:00", verbose_name="Inicio Horas Silenciosas")
    quiet_hours_end = models.TimeField(default="08:00", verbose_name="Fin Horas Silenciosas")
    quiet_hours_enabled = models.BooleanField(default=False, verbose_name="Activar Horas Silenciosas")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Preferencias de Notificación"
        verbose_name_plural = "Preferencias de Notificaciones"
    
    def __str__(self):
        return f"Preferencias de {self.user.username}"
    
    def should_send_notification(self, notification_type, current_time=None):
        """Verifica si se debe enviar una notificación basada en las preferencias"""
        if current_time is None:
            current_time = timezone.now().time()
        
        # Verificar si el tipo de notificación está habilitado
        if notification_type.startswith('visit') and not self.visit_notifications:
            return False
        elif notification_type.startswith('maintenance') and not self.maintenance_notifications:
            return False
        elif notification_type == 'emergency_alert' and not self.emergency_notifications:
            return False
        elif notification_type == 'general_announcement' and not self.general_notifications:
            return False
        
        # Verificar horas silenciosas (excepto emergencias)
        if (self.quiet_hours_enabled and 
            notification_type != 'emergency_alert' and
            self._is_quiet_hours(current_time)):
            return False
        
        return True
    
    def _is_quiet_hours(self, current_time):
        """Verifica si el tiempo actual está en horas silenciosas"""
        if self.quiet_hours_start <= self.quiet_hours_end:
            # Mismo día (ej: 22:00 - 23:00)
            return self.quiet_hours_start <= current_time <= self.quiet_hours_end
        else:
            # Cruza medianoche (ej: 22:00 - 08:00)
            return current_time >= self.quiet_hours_start or current_time <= self.quiet_hours_end
