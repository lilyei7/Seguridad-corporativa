from django.db import models
from django.utils import timezone
from tenants.models import Tenant
from guards.models import Guard


class Visit(models.Model):
    """Modelo para representar las visitas al corporativo"""
    VISIT_STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('en_progreso', 'En Progreso'),
    ]

    VISIT_TYPE_CHOICES = [
        ('trabajo', 'Trabajo'),
        ('entrega', 'Entrega'),
        ('mantenimiento', 'Mantenimiento'),
        ('reunion', 'Reunión'),
        ('personal', 'Personal'),
        ('proveedor', 'Proveedor'),
        ('otro', 'Otro'),
    ]

    # Información del visitante
    visitor_name = models.CharField(max_length=150, verbose_name="Nombre del Visitante")
    visitor_email = models.EmailField(blank=True, verbose_name="Email del Visitante")
    visitor_phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono del Visitante")
    visitor_company = models.CharField(max_length=200, blank=True, verbose_name="Empresa del Visitante")
    visitor_id_number = models.CharField(max_length=50, blank=True, verbose_name="Número de Identificación")
    visitor_photo = models.ImageField(
        upload_to='visitor_photos/%Y/%m/%d/', 
        blank=True, 
        null=True, 
        verbose_name="Foto de Identificación"
    )
    
    # Información de la visita
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name="Inquilino a Visitar")
    visit_type = models.CharField(
        max_length=15, 
        choices=VISIT_TYPE_CHOICES, 
        default='trabajo',
        verbose_name="Tipo de Visita"
    )
    purpose = models.TextField(verbose_name="Propósito de la Visita")
    
    # Fechas y horarios
    scheduled_date = models.DateField(verbose_name="Fecha Programada")
    scheduled_time = models.TimeField(verbose_name="Hora Programada")
    actual_arrival_time = models.DateTimeField(null=True, blank=True, verbose_name="Hora Real de Llegada")
    actual_departure_time = models.DateTimeField(null=True, blank=True, verbose_name="Hora Real de Salida")
    
    # Estado y control
    status = models.CharField(
        max_length=15, 
        choices=VISIT_STATUS_CHOICES, 
        default='pendiente',
        verbose_name="Estado"
    )
    authorized_by = models.CharField(max_length=150, blank=True, verbose_name="Autorizado por")
    registered_by = models.ForeignKey(
        Guard, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='registered_visits',
        verbose_name="Registrado por"
    )
    approved_by = models.ForeignKey(
        Guard, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_visits',
        verbose_name="Aprobado por"
    )
    
    # Información adicional
    notes = models.TextField(blank=True, verbose_name="Notas")
    vehicle_plates = models.CharField(max_length=20, blank=True, verbose_name="Placas del Vehículo")
    items_brought = models.TextField(blank=True, verbose_name="Artículos que Trae")
    items_taken = models.TextField(blank=True, verbose_name="Artículos que Se Lleva")
    
    # Control de tiempo
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"
        ordering = ['-scheduled_date', '-scheduled_time']

    def __str__(self):
        return f"{self.visitor_name} - {self.tenant.tenant_name} ({self.scheduled_date})"

    @property
    def is_overdue(self):
        """Verifica si la visita está atrasada"""
        if self.status == 'pendiente':
            scheduled_datetime = timezone.datetime.combine(
                self.scheduled_date, 
                self.scheduled_time
            )
            scheduled_datetime = timezone.make_aware(scheduled_datetime)
            return timezone.now() > scheduled_datetime
        return False

    def mark_arrived(self, guard=None):
        """Marca la visita como llegada"""
        self.actual_arrival_time = timezone.now()
        self.status = 'en_progreso'
        if guard:
            self.approved_by = guard
        self.save()

    def mark_departed(self):
        """Marca la visita como completada"""
        self.actual_departure_time = timezone.now()
        self.status = 'completada'
        self.save()


class VisitLog(models.Model):
    """Modelo para el registro de actividades de las visitas"""
    ACTION_CHOICES = [
        ('created', 'Creada'),
        ('arrived', 'Llegó'),
        ('departed', 'Se Fue'),
        ('cancelled', 'Cancelada'),
        ('modified', 'Modificada'),
    ]

    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='logs', verbose_name="Visita")
    action = models.CharField(max_length=15, choices=ACTION_CHOICES, verbose_name="Acción")
    performed_by = models.ForeignKey(
        Guard, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Realizado por"
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Registro de Visita"
        verbose_name_plural = "Registros de Visitas"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.visit.visitor_name} - {self.action} ({self.timestamp})"
