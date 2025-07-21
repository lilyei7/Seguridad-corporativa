from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class SecurityCheckpoint(models.Model):
    """Modelo para representar los puntos de seguridad del corporativo"""
    name = models.CharField(max_length=100, verbose_name="Nombre del Punto")
    location = models.CharField(max_length=200, verbose_name="Ubicación")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Punto de Seguridad"
        verbose_name_plural = "Puntos de Seguridad"
        ordering = ['name']

    def __str__(self):
        return self.name


class SecurityIncident(models.Model):
    """Modelo para reportar incidentes de seguridad"""
    INCIDENT_TYPES = [
        ('acceso_no_autorizado', 'Acceso No Autorizado'),
        ('robo', 'Robo'),
        ('vandalismo', 'Vandalismo'),
        ('emergencia_medica', 'Emergencia Médica'),
        ('incendio', 'Incendio'),
        ('falla_equipo', 'Falla de Equipo'),
        ('comportamiento_sospechoso', 'Comportamiento Sospechoso'),
        ('otro', 'Otro'),
    ]

    SEVERITY_LEVELS = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]

    STATUS_CHOICES = [
        ('abierto', 'Abierto'),
        ('en_investigacion', 'En Investigación'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
    ]

    title = models.CharField(max_length=200, verbose_name="Título del Incidente")
    incident_type = models.CharField(
        max_length=30, 
        choices=INCIDENT_TYPES, 
        verbose_name="Tipo de Incidente"
    )
    severity = models.CharField(
        max_length=10, 
        choices=SEVERITY_LEVELS, 
        default='media',
        verbose_name="Severidad"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='abierto',
        verbose_name="Estado"
    )
    description = models.TextField(verbose_name="Descripción del Incidente")
    location = models.CharField(max_length=200, verbose_name="Ubicación")
    checkpoint = models.ForeignKey(
        SecurityCheckpoint, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Punto de Seguridad"
    )
    reported_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='reported_incidents',
        verbose_name="Reportado por"
    )
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_incidents',
        verbose_name="Asignado a"
    )
    incident_datetime = models.DateTimeField(verbose_name="Fecha y Hora del Incidente")
    resolution_notes = models.TextField(blank=True, verbose_name="Notas de Resolución")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Resolución")

    class Meta:
        verbose_name = "Incidente de Seguridad"
        verbose_name_plural = "Incidentes de Seguridad"
        ordering = ['-incident_datetime']

    def __str__(self):
        return f"{self.title} - {self.incident_datetime.strftime('%Y-%m-%d %H:%M')}"


class SystemConfiguration(models.Model):
    """Modelo para configuraciones del sistema"""
    key = models.CharField(max_length=100, unique=True, verbose_name="Clave")
    value = models.TextField(verbose_name="Valor")
    description = models.TextField(blank=True, verbose_name="Descripción")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Actualizado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuraciones del Sistema"
        ordering = ['key']

    def __str__(self):
        return self.key


class SystemThemeConfiguration(models.Model):
    """Configuración de temas y personalización del sistema"""
    
    THEME_CHOICES = [
        ('default', 'Azul Corporativo (Por defecto)'),
        ('green', 'Verde Empresarial'),
        ('purple', 'Púrpura Moderno'),
        ('orange', 'Naranja Energético'),
        ('red', 'Rojo Dinámico'),
        ('indigo', 'Índigo Profesional'),
        ('teal', 'Verde Azulado'),
        ('pink', 'Rosa Creativo'),
    ]
    
    # Información de la empresa
    company_name = models.CharField(
        max_length=200, 
        default='Olcha Tecnología En Seguridad',
        verbose_name="Nombre de la Empresa"
    )
    company_logo = models.ImageField(
        upload_to='configuration/logos/', 
        blank=True, 
        null=True,
        verbose_name="Logo de la Empresa"
    )
    favicon = models.ImageField(
        upload_to='configuration/favicons/', 
        blank=True, 
        null=True,
        verbose_name="Favicon"
    )
    
    # Tema y colores
    theme = models.CharField(
        max_length=20, 
        choices=THEME_CHOICES, 
        default='default',
        verbose_name="Tema del Sistema"
    )
    dark_mode = models.BooleanField(
        default=False,
        verbose_name="Modo Oscuro"
    )
    
    # Colores personalizados (formato hexadecimal)
    hex_validator = RegexValidator(
        regex=r'^#[0-9A-Fa-f]{6}$',
        message='Debe ser un color hexadecimal válido (ej: #FF0000)'
    )
    
    primary_color = models.CharField(
        max_length=7, 
        validators=[hex_validator],
        default='#0ea5e9',
        verbose_name="Color Primario"
    )
    secondary_color = models.CharField(
        max_length=7, 
        validators=[hex_validator],
        default='#0284c7',
        verbose_name="Color Secundario"
    )
    accent_color = models.CharField(
        max_length=7, 
        validators=[hex_validator],
        default='#0369a1',
        verbose_name="Color de Acento"
    )
    
    # Configuración del sidebar
    sidebar_color = models.CharField(
        max_length=7, 
        validators=[hex_validator],
        default='#1e293b',
        verbose_name="Color del Sidebar"
    )
    
    # Configuración de usuario
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Creado por"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Configuración de Tema del Sistema"
        verbose_name_plural = "Configuraciones de Tema del Sistema"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Configuración - {self.company_name} ({self.theme})"
    
    @classmethod
    def get_active_config(cls):
        """Obtiene la configuración activa del sistema"""
        config = cls.objects.filter(is_active=True).first()
        if not config:
            # Crear configuración por defecto si no existe
            from django.contrib.auth.models import User
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                config = cls.objects.create(
                    company_name='Olcha Tecnología En Seguridad',
                    created_by=admin_user,
                    is_active=True
                )
        return config
    
    def get_theme_colors(self):
        """Retorna los colores predefinidos del tema seleccionado"""
        theme_colors = {
            'default': {
                'primary': '#0ea5e9',
                'secondary': '#0284c7', 
                'accent': '#0369a1',
                'sidebar': '#1e293b'
            },
            'green': {
                'primary': '#10b981',
                'secondary': '#059669',
                'accent': '#047857',
                'sidebar': '#064e3b'
            },
            'purple': {
                'primary': '#8b5cf6',
                'secondary': '#7c3aed',
                'accent': '#6d28d9',
                'sidebar': '#581c87'
            },
            'orange': {
                'primary': '#f97316',
                'secondary': '#ea580c',
                'accent': '#c2410c',
                'sidebar': '#9a3412'
            },
            'red': {
                'primary': '#ef4444',
                'secondary': '#dc2626',
                'accent': '#b91c1c',
                'sidebar': '#991b1b'
            },
            'indigo': {
                'primary': '#6366f1',
                'secondary': '#4f46e5',
                'accent': '#4338ca',
                'sidebar': '#312e81'
            },
            'teal': {
                'primary': '#14b8a6',
                'secondary': '#0d9488',
                'accent': '#0f766e',
                'sidebar': '#134e4a'
            },
            'pink': {
                'primary': '#ec4899',
                'secondary': '#db2777',
                'accent': '#be185d',
                'sidebar': '#9d174d'
            }
        }
        return theme_colors.get(self.theme, theme_colors['default'])

    def save(self, *args, **kwargs):
        # Si se marca como activa, desactivar todas las demás
        if self.is_active:
            SystemThemeConfiguration.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


class UserThemePreference(models.Model):
    """Preferencias de tema por usuario"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Usuario"
    )
    dark_mode = models.BooleanField(
        default=False,
        verbose_name="Modo Oscuro"
    )
    preferred_theme = models.CharField(
        max_length=20,
        choices=SystemThemeConfiguration.THEME_CHOICES,
        default='default',
        verbose_name="Tema Preferido"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Preferencia de Tema de Usuario"
        verbose_name_plural = "Preferencias de Tema de Usuarios"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_preferred_theme_display()}"
