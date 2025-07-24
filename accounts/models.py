from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q


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
    """Sistema de notificaciones robusto para diferentes roles"""
    
    NOTIFICATION_TYPES = [
        ('maintenance_request', 'Solicitud de Mantenimiento'),
        ('maintenance_update', 'Actualización de Mantenimiento'),
        ('maintenance_completed', 'Mantenimiento Completado'),
        ('maintenance_rejected', 'Solicitud Rechazada'),
        ('incident_report', 'Reporte de Incidente'),
        ('visit_notification', 'Notificación de Visita'),
        ('visit_approved', 'Visita Aprobada'),
        ('visit_rejected', 'Visita Rechazada'),
        ('system_alert', 'Alerta del Sistema'),
        ('security_alert', 'Alerta de Seguridad'),
        ('payment_reminder', 'Recordatorio de Pago'),
        ('general', 'Notificación General'),
        ('welcome', 'Bienvenida'),
        ('announcement', 'Anuncio'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Crítica'),
        (2, 'Alta'),
        (3, 'Media'),
        (4, 'Baja'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('read', 'Leída'),
        ('dismissed', 'Descartada'),
        ('archived', 'Archivada'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    
    title = models.CharField(max_length=200, verbose_name="Título")
    message = models.TextField(verbose_name="Mensaje")
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default='general')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # URL opcional para acción relacionada con la notificación
    action_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="URL de acción")
    action_text = models.CharField(max_length=100, null=True, blank=True, verbose_name="Texto del botón de acción")
    
    # Metadatos adicionales
    icon = models.CharField(max_length=50, default='fas fa-bell', verbose_name="Icono FontAwesome")
    color = models.CharField(max_length=20, default='blue', verbose_name="Color de la notificación")
    
    # Estados de lectura y procesamiento
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    requires_action = models.BooleanField(default=False, verbose_name="Requiere acción del usuario")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de expiración")
    
    # Agrupación y threads
    thread_key = models.CharField(max_length=100, null=True, blank=True, verbose_name="Clave de hilo")
    parent_notification = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Referencias específicas a objetos relacionados
    maintenance_report = models.ForeignKey(
        'maintenance.MaintenanceReport', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications',
        verbose_name="Reporte de mantenimiento relacionado"
    )
    
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
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['thread_key']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['priority', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Marcar notificación como leída"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.status = 'read'
            self.save()
    
    def dismiss(self):
        """Descartar notificación"""
        self.is_dismissed = True
        self.dismissed_at = timezone.now()
        self.status = 'dismissed'
        self.save()
    
    def archive(self):
        """Archivar notificación"""
        self.status = 'archived'
        self.save()
    
    @property
    def is_urgent(self):
        """Verificar si la notificación es urgente"""
        return self.priority in [1, 2]
    
    @property
    def is_expired(self):
        """Verificar si la notificación ha expirado"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def age_in_hours(self):
        """Obtener la edad de la notificación en horas"""
        return (timezone.now() - self.created_at).total_seconds() / 3600
    
    @property
    def priority_display(self):
        """Obtener el display amigable de la prioridad"""
        return dict(self.PRIORITY_CHOICES).get(self.priority, 'Media')
    
    @property
    def priority_color(self):
        """Obtener el color CSS basado en la prioridad"""
        colors = {
            1: 'red',      # Crítica
            2: 'orange',   # Alta
            3: 'blue',     # Media
            4: 'gray',     # Baja
        }
        return colors.get(self.priority, 'blue')
    
    @property
    def emoji_icon(self):
        """Obtener emoji basado en el tipo de notificación"""
        emojis = {
            'maintenance_request': '🔧',
            'maintenance_update': '🔄',
            'maintenance_completed': '✅',
            'maintenance_rejected': '❌',
            'incident_report': '🚨',
            'visit_notification': '👥',
            'visit_approved': '✅',
            'visit_rejected': '❌',
            'system_alert': '⚠️',
            'security_alert': '🛡️',
            'payment_reminder': '💰',
            'general': '📢',
            'welcome': '👋',
            'announcement': '📣',
        }
        return emojis.get(self.notification_type, '📢')
    
    def create_reply(self, sender, message, **kwargs):
        """Crear una respuesta a esta notificación"""
        return Notification.objects.create(
            recipient=self.sender,  # Responder al remitente original
            sender=sender,
            title=f"Re: {self.title}",
            message=message,
            notification_type=self.notification_type,
            thread_key=self.thread_key or f"thread_{self.id}",
            parent_notification=self,
            **kwargs
        )
    
    @classmethod
    def send_to_admins(cls, title, message, notification_type='general', priority=3, sender=None, **kwargs):
        """Enviar notificación a todos los administradores"""
        admin_users = User.objects.filter(
            Q(is_superuser=True) | 
            Q(user_role__role='admin', user_role__is_active=True)
        ).distinct()
        
        notifications = []
        
        for admin in admin_users:
            notification = cls.objects.create(
                recipient=admin,
                sender=sender,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                **kwargs
            )
            notifications.append(notification)
        
        return notifications
    
    @classmethod
    def send_to_tenant(cls, tenant_user, title, message, notification_type='general', priority=3, sender=None, **kwargs):
        """Enviar notificación a un inquilino específico"""
        return cls.objects.create(
            recipient=tenant_user,
            sender=sender,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            **kwargs
        )
    
    @classmethod
    def broadcast_to_role(cls, role, title, message, notification_type='general', priority=3, sender=None, **kwargs):
        """Enviar notificación a todos los usuarios de un rol específico"""
        users = User.objects.filter(user_role__role=role, user_role__is_active=True)
        notifications = []
        
        for user in users:
            notification = cls.objects.create(
                recipient=user,
                sender=sender,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                **kwargs
            )
            notifications.append(notification)
        
        return notifications
    
    @classmethod
    def send_maintenance_request(cls, sender, title, message, maintenance_obj=None, **kwargs):
        """Enviar solicitud de mantenimiento a los administradores"""
        from django.contrib.contenttypes.models import ContentType
        
        notifications = cls.send_to_admins(
            title=f"🔧 Nueva Solicitud: {title}",
            message=message,
            notification_type='maintenance_request',
            priority=2,  # Alta prioridad
            sender=sender,
            requires_action=True,
            action_text="Ver Solicitud",
            icon="fas fa-tools",
            color="orange",
            thread_key=f"maintenance_{maintenance_obj.id if maintenance_obj else 'unknown'}",
            **kwargs
        )
        
        # Si hay un objeto de mantenimiento, agregar referencia
        if maintenance_obj:
            content_type = ContentType.objects.get_for_model(maintenance_obj)
            for notification in notifications:
                notification.content_type = content_type
                notification.object_id = maintenance_obj.id
                notification.save()
        
        return notifications
    
    @classmethod
    def send_maintenance_update(cls, maintenance_obj, tenant_user, title, message, sender=None, **kwargs):
        """Enviar actualización de mantenimiento al inquilino"""
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(maintenance_obj)
        
        return cls.send_to_tenant(
            tenant_user=tenant_user,
            title=f"� Actualización: {title}",
            message=message,
            notification_type='maintenance_update',
            priority=3,  # Prioridad media
            sender=sender,
            action_text="Ver Detalles",
            icon="fas fa-sync-alt",
            color="blue",
            thread_key=f"maintenance_{maintenance_obj.id}",
            content_type=content_type,
            object_id=maintenance_obj.id,
            **kwargs
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
