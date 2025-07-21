from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserRole(models.Model):
    """Modelo para definir los roles de usuario en el sistema"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('tenant', 'Inquilino'),
        ('guard', 'Vigilante'),
        ('maintenance', 'Personal de Mantenimiento'),
        ('reception', 'Recepcionista'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Campos específicos según el rol
    tenant_profile = models.OneToOneField(
        'tenants.Tenant', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='user_profile'
    )
    guard_profile = models.OneToOneField(
        'guards.Guard', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='user_profile'
    )
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def can_view_all_tenants(self):
        """Solo admin puede ver todos los inquilinos"""
        return self.role == 'admin'
    
    @property
    def can_view_all_guards(self):
        """Solo admin puede ver todos los vigilantes"""
        return self.role == 'admin'
    
    @property
    def can_view_security_cameras(self):
        """Solo admin y vigilantes pueden ver cámaras"""
        return self.role in ['admin', 'guard']
    
    @property
    def can_manage_system_config(self):
        """Solo admin puede gestionar configuración del sistema"""
        return self.role == 'admin'
    
    @property
    def can_create_visits(self):
        """Inquilinos y admin pueden crear visitas"""
        return self.role in ['admin', 'tenant', 'reception']
    
    @property
    def can_view_maintenance_reports(self):
        """Admin y personal de mantenimiento pueden ver todos los reportes"""
        return self.role in ['admin', 'maintenance']
    
    @property
    def can_create_maintenance_reports(self):
        """Todos pueden crear reportes de mantenimiento"""
        return True
    
    @property
    def can_assign_guards_to_points(self):
        """Solo admin puede asignar vigilantes a puntos"""
        return self.role == 'admin'


class Notification(models.Model):
    """Sistema de notificaciones para diferentes roles"""
    
    NOTIFICATION_TYPES = [
        ('maintenance_request', 'Solicitud de Mantenimiento'),
        ('incident_report', 'Reporte de Incidente'),
        ('visit_notification', 'Notificación de Visita'),
        ('system_alert', 'Alerta del Sistema'),
        ('security_alert', 'Alerta de Seguridad'),
        ('general', 'Notificación General'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    
    title = models.CharField(max_length=200, verbose_name="Título")
    message = models.TextField(verbose_name="Mensaje")
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default='general')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Referencia opcional al objeto relacionado
    content_type = models.ForeignKey(
        'contenttypes.ContentType', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Marcar notificación como leída"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    @classmethod
    def send_to_admins(cls, title, message, notification_type='general', priority='medium', sender=None):
        """Enviar notificación a todos los administradores"""
        admin_users = User.objects.filter(user_role__role='admin', user_role__is_active=True)
        notifications = []
        
        for admin in admin_users:
            notification = cls.objects.create(
                recipient=admin,
                sender=sender,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority
            )
            notifications.append(notification)
        
        return notifications
    
    @classmethod
    def send_maintenance_request(cls, sender, title, message):
        """Enviar solicitud de mantenimiento a los administradores"""
        return cls.send_to_admins(
            title=f"🔧 Solicitud de Mantenimiento: {title}",
            message=message,
            notification_type='maintenance_request',
            priority='medium',
            sender=sender
        )
    
    @classmethod
    def send_incident_report(cls, sender, title, message, priority='high'):
        """Enviar reporte de incidente"""
        return cls.send_to_admins(
            title=f"🚨 Reporte de Incidente: {title}",
            message=message,
            notification_type='incident_report',
            priority=priority,
            sender=sender
        )


class UserPreferences(models.Model):
    """Preferencias específicas del usuario"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Preferencias de notificaciones
    email_notifications = models.BooleanField(default=True, verbose_name="Notificaciones por email")
    push_notifications = models.BooleanField(default=True, verbose_name="Notificaciones push")
    sms_notifications = models.BooleanField(default=False, verbose_name="Notificaciones SMS")
    
    # Preferencias de interfaz
    dashboard_layout = models.CharField(
        max_length=20, 
        choices=[
            ('compact', 'Compacto'),
            ('standard', 'Estándar'),
            ('expanded', 'Expandido')
        ],
        default='standard'
    )
    
    items_per_page = models.IntegerField(default=25, verbose_name="Elementos por página")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Preferencias de Usuario"
        verbose_name_plural = "Preferencias de Usuarios"
    
    def __str__(self):
        return f"Preferencias de {self.user.username}"
