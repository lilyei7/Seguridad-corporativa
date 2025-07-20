from django.db import models
from django.contrib.auth.models import User


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
