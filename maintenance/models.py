from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class MaintenanceArea(models.Model):
    """Modelo para representar las áreas que requieren mantenimiento"""
    AREA_TYPE_CHOICES = [
        ('estructural', 'Estructural'),
        ('mecanico', 'Mecánico'),
        ('electrico', 'Eléctrico'),
        ('sistemas', 'Sistemas'),
        ('seguridad', 'Seguridad'),
        ('limpieza', 'Limpieza'),
        ('otro', 'Otro'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nombre del área")
    location = models.CharField(max_length=200, verbose_name="Ubicación")
    floor = models.CharField(max_length=50, blank=True, verbose_name="Piso/Nivel")
    description = models.TextField(blank=True, verbose_name="Descripción")
    area_type = models.CharField(
        max_length=20, 
        choices=AREA_TYPE_CHOICES, 
        default='otro',
        verbose_name="Tipo de área"
    )
    responsible_person = models.CharField(max_length=100, blank=True, verbose_name="Responsable del área")
    contact_info = models.CharField(max_length=200, blank=True, verbose_name="Información de contacto")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Área de Mantenimiento"
        verbose_name_plural = "Áreas de Mantenimiento"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.location}"
    
    def get_status_badge_color(self):
        """Retorna las clases CSS para el badge de estado"""
        if self.checklists.filter(status='in_progress').exists():
            return 'bg-blue-100 text-blue-800'
        elif self.cameras.filter(status='offline').exists():
            return 'bg-red-100 text-red-800'
        elif self.cameras.filter(status='active').exists():
            return 'bg-green-100 text-green-800'
        else:
            return 'bg-gray-100 text-gray-800'
    
    def get_status_display(self):
        """Retorna el estado del área basado en sus componentes"""
        if self.checklists.filter(status='in_progress').exists():
            return 'En Mantenimiento'
        elif self.cameras.filter(status='offline').exists():
            return 'Atención Requerida'
        elif self.cameras.filter(status='active').exists():
            return 'Operativa'
        else:
            return 'Inactiva'
    
    @property
    def checklists_count(self):
        """Retorna el número de checklists en el área"""
        return self.checklists.count()
    
    @property
    def cameras_count(self):
        """Retorna el número de cámaras en el área"""
        return self.cameras.count()
    
    @property
    def active_cameras_count(self):
        """Retorna el número de cámaras activas en el área"""
        return self.cameras.filter(status='active').count()


class MaintenanceChecklist(models.Model):
    """Modelo para representar un checklist de mantenimiento"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]

    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    area = models.ForeignKey(
        MaintenanceArea, 
        on_delete=models.CASCADE, 
        related_name='checklists',
        verbose_name="Área"
    )
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_checklists',
        verbose_name="Asignado a"
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='created_checklists',
        verbose_name="Creado por"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name="Estado"
    )
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='medium',
        verbose_name="Prioridad"
    )
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha límite")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de completado")
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Checklist de Mantenimiento"
        verbose_name_plural = "Checklists de Mantenimiento"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.area.name}"
    
    def get_status_display_color(self):
        """Retorna las clases CSS para el color del estado"""
        colors = {
            'pendiente': 'bg-yellow-100 text-yellow-800',
            'en_proceso': 'bg-blue-100 text-blue-800',
            'completado': 'bg-green-100 text-green-800',
            'requiere_atencion': 'bg-red-100 text-red-800',
            'cancelado': 'bg-gray-100 text-gray-800',
        }
        return colors.get(self.status, 'bg-gray-100 text-gray-800')
    
    def get_priority_display_color(self):
        """Retorna las clases CSS para el color de la prioridad"""
        colors = {
            1: 'bg-red-100 text-red-800',      # Crítica
            2: 'bg-orange-100 text-orange-800', # Alta
            3: 'bg-blue-100 text-blue-800',     # Media
            4: 'bg-gray-100 text-gray-800',     # Baja
        }
        return colors.get(self.priority, 'bg-gray-100 text-gray-800')
    
    @property
    def completion_percentage(self):
        """Calcula el porcentaje de completitud del checklist"""
        total_items = self.items.count()
        if total_items == 0:
            return 0
        completed_items = self.items.filter(is_completed=True).count()
        return round((completed_items / total_items) * 100)
    
    @property
    def completed_items_count(self):
        """Retorna el número de elementos completados"""
        return self.items.filter(is_completed=True).count()
    
    @property
    def pending_items_count(self):
        """Retorna el número de elementos pendientes"""
        return self.items.filter(is_completed=False).count()
    
    @property
    def total_evidences_count(self):
        """Retorna el total de evidencias subidas"""
        return MaintenanceEvidence.objects.filter(item__checklist=self).count()

    def save(self, *args, **kwargs):
        # Auto-completar cuando todos los elementos están completados
        if self.pk and self.status != 'completed':
            total_items = self.items.count()
            if total_items > 0:
                completed_items = self.items.filter(is_completed=True).count()
                if completed_items == total_items:
                    self.status = 'completed'
                    self.completed_at = timezone.now()
        super().save(*args, **kwargs)


class MaintenanceItem(models.Model):
    """Modelo para representar elementos individuales de un checklist"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('skipped', 'Omitido'),
    ]
    
    checklist = models.ForeignKey(
        MaintenanceChecklist, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name="Checklist"
    )
    item_name = models.CharField(max_length=200, verbose_name="Nombre del item")
    description = models.TextField(verbose_name="Descripción")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name="Estado"
    )
    observations = models.TextField(blank=True, verbose_name="Observaciones")
    notes = models.TextField(blank=True, verbose_name="Notas")
    is_completed = models.BooleanField(default=False, verbose_name="Completado")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de completado")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Elemento de Checklist"
        verbose_name_plural = "Elementos de Checklist"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.checklist.title} - {self.item_name}"

    def save(self, *args, **kwargs):
        # Sincronizar is_completed con status
        if self.status == 'completed' and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
        elif self.status != 'completed' and self.is_completed:
            self.is_completed = False
            self.completed_at = None
        super().save(*args, **kwargs)


class MaintenanceEvidence(models.Model):
    """Modelo para almacenar evidencias fotográficas del mantenimiento"""
    EVIDENCE_TYPE_CHOICES = [
        ('before', 'Antes'),
        ('after', 'Después'),
        ('problem', 'Problema'),
        ('solution', 'Solución'),
        ('progress', 'En Progreso'),
    ]

    item = models.ForeignKey(
        MaintenanceItem, 
        on_delete=models.CASCADE, 
        related_name='evidences',
        verbose_name="Elemento"
    )
    evidence_type = models.CharField(
        max_length=20, 
        choices=EVIDENCE_TYPE_CHOICES,
        verbose_name="Tipo de evidencia"
    )
    image = models.ImageField(
        upload_to='maintenance/evidences/%Y/%m/', 
        verbose_name="Imagen"
    )
    description = models.TextField(blank=True, verbose_name="Descripción")
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Subido por"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de subida")

    class Meta:
        verbose_name = "Evidencia de Mantenimiento"
        verbose_name_plural = "Evidencias de Mantenimiento"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.item.checklist.title} - {self.get_evidence_type_display()}"


class Camera(models.Model):
    """Modelo para representar las cámaras de seguridad"""
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('offline', 'Fuera de línea'),
        ('maintenance', 'Mantenimiento'),
        ('inactive', 'Inactiva'),
    ]
    
    CAMERA_TYPE_CHOICES = [
        ('dome', 'Domo'),
        ('bullet', 'Bala'),
        ('ptz', 'PTZ'),
        ('fisheye', 'Ojo de Pez'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nombre")
    code = models.CharField(max_length=50, unique=True, verbose_name="Código")
    area = models.ForeignKey(
        MaintenanceArea, 
        on_delete=models.CASCADE, 
        related_name='cameras',
        verbose_name="Área"
    )
    location = models.CharField(max_length=200, verbose_name="Ubicación específica")
    floor = models.CharField(max_length=50, blank=True, verbose_name="Piso/Nivel")
    camera_type = models.CharField(
        max_length=20, 
        choices=CAMERA_TYPE_CHOICES, 
        default='dome',
        verbose_name="Tipo de cámara"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    port = models.PositiveIntegerField(null=True, blank=True, verbose_name="Puerto")
    stream_url = models.URLField(blank=True, verbose_name="URL del stream")
    resolution = models.CharField(max_length=20, blank=True, verbose_name="Resolución")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        verbose_name="Estado"
    )
    is_recording = models.BooleanField(default=True, verbose_name="Grabando")
    description = models.TextField(blank=True, verbose_name="Descripción")
    installation_date = models.DateField(null=True, blank=True, verbose_name="Fecha de instalación")
    last_maintenance = models.DateField(null=True, blank=True, verbose_name="Último mantenimiento")
    responsible_person = models.CharField(max_length=100, blank=True, verbose_name="Responsable")
    last_check = models.DateTimeField(auto_now=True, verbose_name="Última verificación")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Cámara de Seguridad"
        verbose_name_plural = "Cámaras de Seguridad"
        ordering = ['area', 'name']

    def __str__(self):
        return f"{self.name} - {self.area.name}"
    
    def get_status_badge_color(self):
        """Retorna las clases CSS para el badge de estado"""
        colors = {
            'active': 'bg-green-100 text-green-800',
            'offline': 'bg-red-100 text-red-800',
            'maintenance': 'bg-yellow-100 text-yellow-800',
            'inactive': 'bg-gray-100 text-gray-800',
        }
        return colors.get(self.status, 'bg-gray-100 text-gray-800')
