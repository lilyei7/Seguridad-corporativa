from django.db import models
from django.contrib.auth.models import User


class Tenant(models.Model):
    """Modelo para representar los inquilinos del corporativo"""
    
    # Información Básica
    tenant_name = models.CharField(max_length=200, verbose_name="Nombre del Inquilino")
    razon_social = models.CharField(max_length=250, verbose_name="Razón Social", default="")
    representante_legal = models.CharField(max_length=200, verbose_name="Representante Legal", default="")
    
    # Información de Contacto
    contact_person = models.CharField(max_length=150, verbose_name="Persona de Contacto")
    contact_email = models.EmailField(verbose_name="Email de Contacto")
    contact_phone = models.CharField(max_length=20, verbose_name="Teléfono de Contacto")
    telefono_oficina = models.CharField(max_length=20, verbose_name="Número de Teléfono de Oficina", default="")
    correo_recepcion = models.EmailField(verbose_name="Correo de Recepción de Oficina", blank=True, null=True)
    
    # Información de Ubicación
    address = models.TextField(verbose_name="Dirección")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    state = models.CharField(max_length=100, verbose_name="Estado")
    zip_code = models.CharField(max_length=10, verbose_name="Código Postal")
    
    # Información de Oficina
    piso = models.CharField(max_length=50, verbose_name="Piso", default="")
    numero_oficina = models.CharField(max_length=50, verbose_name="Número de Oficina", default="")
    metros_cuadrados = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name="Metros Cuadrados (m²)",
        default=0.00
    )
    
    TIPO_OFICINA_CHOICES = [
        ('privada', 'Oficina Privada'),
        ('compartida', 'Oficina Compartida'),
        ('coworking', 'Espacio Coworking'),
        ('ejecutiva', 'Oficina Ejecutiva'),
        ('virtual', 'Oficina Virtual'),
        ('sala_juntas', 'Sala de Juntas'),
    ]
    
    tipo_oficina = models.CharField(
        max_length=20, 
        choices=TIPO_OFICINA_CHOICES,
        verbose_name="Tipo de Oficina",
        default='privada'
    )
    
    # Servicios
    recibo_luz = models.TextField(
        verbose_name="Recibo de Luz (Información)",
        help_text="Información adicional sobre el recibo de luz",
        blank=True,
        null=True
    )
    
    # Sistema
    assigned_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Usuario Asignado"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Inquilino"
        verbose_name_plural = "Inquilinos"
        ordering = ['tenant_name']

    def __str__(self):
        return f"{self.tenant_name} - {self.numero_oficina}"
