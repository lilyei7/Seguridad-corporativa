from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SecurityPoint(models.Model):
    """Modelo para representar los puntos de seguridad del edificio"""
    POINT_STATUS_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('mantenimiento', 'En Mantenimiento'),
    ]
    
    POINT_TYPE_CHOICES = [
        ('entrada_principal', 'Entrada Principal'),
        ('entrada_secundaria', 'Entrada Secundaria'),
        ('estacionamiento', 'Estacionamiento'),
        ('piso', 'Punto de Piso'),
        ('escalera_emergencia', 'Escalera de Emergencia'),
        ('azotea', 'Azotea'),
        ('sotano', 'Sótano'),
        ('perimetro', 'Perímetro'),
        ('sala_sistemas', 'Sala de Sistemas'),
        ('recepcion', 'Recepción'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nombre del Punto")
    code = models.CharField(max_length=10, unique=True, verbose_name="Código del Punto")
    point_type = models.CharField(
        max_length=25, 
        choices=POINT_TYPE_CHOICES, 
        verbose_name="Tipo de Punto"
    )
    location = models.CharField(max_length=200, verbose_name="Ubicación Detallada")
    floor = models.CharField(max_length=20, verbose_name="Piso/Nivel")
    description = models.TextField(verbose_name="Descripción", blank=True)
    status = models.CharField(
        max_length=15, 
        choices=POINT_STATUS_CHOICES, 
        default='activo',
        verbose_name="Estado"
    )
    priority = models.IntegerField(
        default=1, 
        verbose_name="Prioridad",
        help_text="1=Muy Alta, 2=Alta, 3=Media, 4=Baja, 5=Muy Baja"
    )
    check_frequency_minutes = models.IntegerField(
        default=60, 
        verbose_name="Frecuencia de Revisión (minutos)"
    )
    qr_code = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Código QR",
        help_text="Código QR para verificación del punto"
    )
    photo = models.ImageField(
        upload_to='security_points/', 
        blank=True, 
        null=True, 
        verbose_name="Foto del Punto"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Punto de Seguridad"
        verbose_name_plural = "Puntos de Seguridad"
        ordering = ['priority', 'floor', 'name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def priority_display(self):
        priorities = {
            1: "Muy Alta",
            2: "Alta", 
            3: "Media",
            4: "Baja",
            5: "Muy Baja"
        }
        return priorities.get(self.priority, "Sin definir")

    @property
    def priority_color(self):
        colors = {
            1: "red",
            2: "orange", 
            3: "yellow",
            4: "blue",
            5: "gray"
        }
        return colors.get(self.priority, "gray")


class SecurityRoute(models.Model):
    """Modelo para representar las rutas de rondín de seguridad"""
    ROUTE_STATUS_CHOICES = [
        ('activa', 'Activa'),
        ('inactiva', 'Inactiva'),
        ('temporal', 'Temporal'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nombre de la Ruta")
    code = models.CharField(max_length=10, unique=True, verbose_name="Código de Ruta")
    description = models.TextField(verbose_name="Descripción", blank=True)
    status = models.CharField(
        max_length=15, 
        choices=ROUTE_STATUS_CHOICES, 
        default='activa',
        verbose_name="Estado"
    )
    estimated_duration_minutes = models.IntegerField(
        default=30, 
        verbose_name="Duración Estimada (minutos)"
    )
    security_points = models.ManyToManyField(
        SecurityPoint,
        through='RoutePoint',
        verbose_name="Puntos de Seguridad"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Ruta de Seguridad"
        verbose_name_plural = "Rutas de Seguridad"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def total_points(self):
        return self.security_points.count()


class RoutePoint(models.Model):
    """Modelo intermedio para ordenar los puntos en una ruta"""
    route = models.ForeignKey(SecurityRoute, on_delete=models.CASCADE)
    security_point = models.ForeignKey(SecurityPoint, on_delete=models.CASCADE)
    order = models.IntegerField(verbose_name="Orden en la Ruta")
    estimated_time_minutes = models.IntegerField(
        default=5, 
        verbose_name="Tiempo Estimado en el Punto (minutos)"
    )

    class Meta:
        ordering = ['order']
        unique_together = ['route', 'order']

    def __str__(self):
        return f"{self.route.code} - {self.security_point.code} (#{self.order})"


class Guard(models.Model):
    """Modelo para representar los vigilantes"""
    GUARD_STATUS_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
        ('vacaciones', 'Vacaciones'),
    ]
    
    POSITION_CHOICES = [
        ('vigilante', 'Vigilante'),
        ('supervisor', 'Supervisor'),
        ('jefe_seguridad', 'Jefe de Seguridad'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario")
    employee_id = models.CharField(max_length=20, unique=True, verbose_name="ID de Empleado")
    position = models.CharField(
        max_length=20, 
        choices=POSITION_CHOICES, 
        default='vigilante',
        verbose_name="Puesto"
    )
    status = models.CharField(
        max_length=15, 
        choices=GUARD_STATUS_CHOICES, 
        default='activo',
        verbose_name="Estado"
    )
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    emergency_contact = models.CharField(max_length=150, verbose_name="Contacto de Emergencia")
    emergency_phone = models.CharField(max_length=20, verbose_name="Teléfono de Emergencia")
    hire_date = models.DateField(verbose_name="Fecha de Contratación")
    photo = models.ImageField(upload_to='guards/', blank=True, null=True, verbose_name="Foto")
    assigned_routes = models.ManyToManyField(
        SecurityRoute,
        blank=True,
        verbose_name="Rutas Asignadas",
        help_text="Rutas de rondín asignadas a este vigilante"
    )
    assigned_points = models.ManyToManyField(
        SecurityPoint,
        blank=True,
        verbose_name="Puntos Asignados",
        help_text="Puntos de seguridad específicos asignados"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Vigilante"
        verbose_name_plural = "Vigilantes"
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

    @property
    def full_name(self):
        return self.user.get_full_name()


class Shift(models.Model):
    """Modelo para representar los turnos de trabajo"""
    SHIFT_TYPES = [
        ('matutino', 'Matutino (6:00 - 14:00)'),
        ('vespertino', 'Vespertino (14:00 - 22:00)'),
        ('nocturno', 'Nocturno (22:00 - 6:00)'),
    ]

    guard = models.ForeignKey(Guard, on_delete=models.CASCADE, verbose_name="Vigilante")
    shift_type = models.CharField(max_length=15, choices=SHIFT_TYPES, verbose_name="Tipo de Turno")
    date = models.DateField(verbose_name="Fecha")
    start_time = models.TimeField(verbose_name="Hora de Inicio")
    end_time = models.TimeField(verbose_name="Hora de Fin")
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        ordering = ['-date', 'start_time']

    def __str__(self):
        return f"{self.guard.full_name} - {self.shift_type} ({self.date})"


class PatrolRound(models.Model):
    """Modelo para registrar los rondines de seguridad"""
    ROUND_STATUS_CHOICES = [
        ('iniciado', 'Iniciado'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('interrumpido', 'Interrumpido'),
        ('cancelado', 'Cancelado'),
    ]

    guard = models.ForeignKey(Guard, on_delete=models.CASCADE, verbose_name="Vigilante")
    route = models.ForeignKey(SecurityRoute, on_delete=models.CASCADE, verbose_name="Ruta")
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, verbose_name="Turno", null=True, blank=True)
    status = models.CharField(
        max_length=15, 
        choices=ROUND_STATUS_CHOICES, 
        default='iniciado',
        verbose_name="Estado"
    )
    start_time = models.DateTimeField(verbose_name="Hora de Inicio")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Hora de Fin")
    total_points_checked = models.IntegerField(default=0, verbose_name="Puntos Verificados")
    incidents_reported = models.IntegerField(default=0, verbose_name="Incidentes Reportados")
    notes = models.TextField(blank=True, verbose_name="Observaciones Generales")
    weather_conditions = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Condiciones Climáticas"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Rondín de Patrullaje"
        verbose_name_plural = "Rondines de Patrullaje"
        ordering = ['-start_time']

    def __str__(self):
        return f"Rondín {self.route.code} - {self.guard.full_name} ({self.start_time.strftime('%d/%m/%Y %H:%M')})"

    @property
    def duration_minutes(self):
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return None

    @property
    def is_active(self):
        return self.status in ['iniciado', 'en_progreso']


class PointCheck(models.Model):
    """Modelo para registrar la verificación de cada punto durante un rondín"""
    CHECK_STATUS_CHOICES = [
        ('normal', 'Normal'),
        ('anormal', 'Anormal'),
        ('no_verificado', 'No Verificado'),
        ('no_accesible', 'No Accesible'),
    ]

    patrol_round = models.ForeignKey(
        PatrolRound, 
        on_delete=models.CASCADE, 
        verbose_name="Rondín",
        related_name='point_checks'
    )
    security_point = models.ForeignKey(SecurityPoint, on_delete=models.CASCADE, verbose_name="Punto de Seguridad")
    check_time = models.DateTimeField(verbose_name="Hora de Verificación")
    status = models.CharField(
        max_length=15, 
        choices=CHECK_STATUS_CHOICES, 
        default='normal',
        verbose_name="Estado del Punto"
    )
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    photo = models.ImageField(
        upload_to='point_checks/', 
        blank=True, 
        null=True, 
        verbose_name="Foto de Evidencia"
    )
    qr_verified = models.BooleanField(default=False, verbose_name="QR Verificado")
    temperature = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Temperatura (°C)"
    )
    humidity = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Humedad (%)"
    )
    
    class Meta:
        verbose_name = "Verificación de Punto"
        verbose_name_plural = "Verificaciones de Puntos"
        ordering = ['check_time']

    def __str__(self):
        return f"{self.security_point.code} - {self.check_time.strftime('%H:%M')} ({self.status})"


class SecurityIncident(models.Model):
    """Modelo para reportar incidentes de seguridad"""
    INCIDENT_TYPE_CHOICES = [
        ('acceso_no_autorizado', 'Acceso No Autorizado'),
        ('equipo_danado', 'Equipo Dañado'),
        ('falla_sistema', 'Falla de Sistema'),
        ('persona_sospechosa', 'Persona Sospechosa'),
        ('alarma', 'Activación de Alarma'),
        ('emergencia_medica', 'Emergencia Médica'),
        ('incendio', 'Incendio'),
        ('robo', 'Robo'),
        ('vandalismo', 'Vandalismo'),
        ('otro', 'Otro'),
    ]

    SEVERITY_CHOICES = [
        (1, 'Crítico'),
        (2, 'Alto'),
        (3, 'Medio'),
        (4, 'Bajo'),
        (5, 'Informativo'),
    ]

    guard = models.ForeignKey(Guard, on_delete=models.CASCADE, verbose_name="Vigilante Reporta")
    point_check = models.ForeignKey(
        PointCheck, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        verbose_name="Verificación de Punto"
    )
    security_point = models.ForeignKey(SecurityPoint, on_delete=models.CASCADE, verbose_name="Punto de Seguridad")
    incident_type = models.CharField(max_length=25, choices=INCIDENT_TYPE_CHOICES, verbose_name="Tipo de Incidente")
    severity = models.IntegerField(choices=SEVERITY_CHOICES, default=3, verbose_name="Severidad")
    title = models.CharField(max_length=200, verbose_name="Título del Incidente")
    description = models.TextField(verbose_name="Descripción Detallada")
    actions_taken = models.TextField(blank=True, verbose_name="Acciones Tomadas")
    photo = models.ImageField(
        upload_to='incidents/', 
        blank=True, 
        null=True, 
        verbose_name="Foto de Evidencia"
    )
    resolved = models.BooleanField(default=False, verbose_name="Resuelto")
    resolved_by = models.ForeignKey(
        Guard, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='incidents_resolved',
        verbose_name="Resuelto por"
    )
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Resolución")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Reporte")

    class Meta:
        verbose_name = "Incidente de Seguridad"
        verbose_name_plural = "Incidentes de Seguridad"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.security_point.code} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"

    @property
    def severity_display(self):
        severities = dict(self.SEVERITY_CHOICES)
        return severities.get(self.severity, "Sin definir")

    @property
    def severity_color(self):
        colors = {
            1: "red",
            2: "orange", 
            3: "yellow",
            4: "blue",
            5: "gray"
        }
        return colors.get(self.severity, "gray")
