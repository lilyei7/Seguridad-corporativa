from django import forms
from django.contrib.auth.models import User
from django.db import models
from .models import (
    MaintenanceArea, MaintenanceChecklist, MaintenanceItem, 
    MaintenanceEvidence, Camera, MaintenanceReport, MaintenanceReportImage
)


class MaintenanceAreaForm(forms.ModelForm):
    """Formulario para crear/editar áreas de mantenimiento"""
    
    class Meta:
        model = MaintenanceArea
        fields = [
            'name', 'area_type', 'location', 'floor', 'description',
            'responsible_person', 'contact_info'
        ]
        labels = {
            'name': 'Nombre del Área',
            'area_type': 'Tipo de Área',
            'location': 'Ubicación',
            'floor': 'Piso/Nivel',
            'description': 'Descripción',
            'responsible_person': 'Responsable del Área',
            'contact_info': 'Información de Contacto',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'area_type': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            })


class MaintenanceChecklistForm(forms.ModelForm):
    """Formulario para crear/editar checklists de mantenimiento"""
    
    class Meta:
        model = MaintenanceChecklist
        fields = [
            'title', 'description', 'area', 'assigned_to', 
            'priority', 'due_date', 'notes'
        ]
        labels = {
            'title': 'Título del Checklist',
            'description': 'Descripción',
            'area': 'Área',
            'assigned_to': 'Asignar a',
            'priority': 'Prioridad',
            'due_date': 'Fecha Límite',
            'notes': 'Notas Adicionales',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'area': forms.Select(),
            'assigned_to': forms.Select(),
            'priority': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar usuarios que pueden ser asignados
        self.fields['assigned_to'].queryset = User.objects.filter(
            models.Q(is_superuser=True) | 
            models.Q(groups__name__in=['Vigilantes', 'Mantenimiento'])
        ).distinct().order_by('first_name', 'last_name')
        
        # Filtrar áreas activas
        self.fields['area'].queryset = MaintenanceArea.objects.filter(
            is_active=True
        ).order_by('name')
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            })


class MaintenanceItemForm(forms.ModelForm):
    """Formulario para crear/editar items de checklist"""
    
    class Meta:
        model = MaintenanceItem
        fields = ['item_name', 'description', 'status', 'observations']
        labels = {
            'item_name': 'Nombre del Item',
            'description': 'Descripción',
            'status': 'Estado',
            'observations': 'Observaciones',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'observations': forms.Textarea(attrs={'rows': 3}),
            'status': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            })


class MaintenanceEvidenceForm(forms.ModelForm):
    """Formulario para subir evidencias fotográficas"""
    
    class Meta:
        model = MaintenanceEvidence
        fields = ['evidence_type', 'image', 'description']
        labels = {
            'evidence_type': 'Tipo de Evidencia',
            'image': 'Imagen',
            'description': 'Descripción de la Evidencia',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'evidence_type': forms.Select(),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'image':
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                    'accept': 'image/*'
                })
            else:
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
                })


class CameraForm(forms.ModelForm):
    """Formulario para crear/editar cámaras"""
    
    class Meta:
        model = Camera
        fields = [
            'name', 'code', 'camera_type', 'location', 'floor',
            'ip_address', 'port', 'stream_url', 'status', 'description',
            'installation_date', 'last_maintenance', 'responsible_person',
            'is_recording'
        ]
        labels = {
            'name': 'Nombre de la Cámara',
            'code': 'Código de la Cámara',
            'camera_type': 'Tipo de Cámara',
            'location': 'Ubicación',
            'floor': 'Piso/Nivel',
            'ip_address': 'Dirección IP',
            'port': 'Puerto',
            'stream_url': 'URL del Stream',
            'status': 'Estado',
            'description': 'Descripción',
            'installation_date': 'Fecha de Instalación',
            'last_maintenance': 'Último Mantenimiento',
            'responsible_person': 'Responsable',
            'is_recording': 'Grabando',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'installation_date': forms.DateInput(attrs={'type': 'date'}),
            'last_maintenance': forms.DateInput(attrs={'type': 'date'}),
            'camera_type': forms.Select(),
            'status': forms.Select(),
            'is_recording': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
                })
            else:
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
                })


class QuickItemStatusForm(forms.Form):
    """Formulario rápido para actualizar el estado de un item"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('skipped', 'Omitido'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label='Estado',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
        })
    )
    observations = forms.CharField(
        required=False,
        label='Observaciones',
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
        })
    )


class ChecklistFilterForm(forms.Form):
    """Formulario para filtrar checklists"""
    STATUS_CHOICES = [('', 'Todos los estados')] + MaintenanceChecklist.STATUS_CHOICES
    PRIORITY_CHOICES = [('', 'Todas las prioridades')] + MaintenanceChecklist.PRIORITY_CHOICES
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        label='Estado',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
        })
    )
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        label='Prioridad',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
        })
    )
    area = forms.ModelChoiceField(
        queryset=MaintenanceArea.objects.filter(is_active=True),
        required=False,
        empty_label="Todas las áreas",
        label='Área',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
        })
    )
    search = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por título, descripción o área...',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
        })
    )


class MaintenanceReportForm(forms.ModelForm):
    """Formulario para que los inquilinos reporten problemas de mantenimiento"""
    
    class Meta:
        model = MaintenanceReport
        fields = [
            'title', 'description', 'category', 'area', 'priority',
            'specific_location', 'contact_phone', 'contact_email', 
            'available_times'
        ]
        labels = {
            'title': 'Título del Reporte',
            'description': 'Descripción del Problema',
            'category': 'Categoría',
            'area': 'Área del Edificio',
            'priority': 'Prioridad',
            'specific_location': 'Ubicación Específica',
            'contact_phone': 'Teléfono de Contacto',
            'contact_email': 'Email de Contacto',
            'available_times': 'Horarios Disponibles para Acceso',
        }
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe detalladamente el problema que requiere atención...'
            }),
            'specific_location': forms.TextInput(attrs={
                'placeholder': 'Ej: Oficina 201, Baño del 3er piso, Recepción...'
            }),
            'contact_phone': forms.TextInput(attrs={
                'placeholder': 'Ej: +57 300 123 4567'
            }),
            'contact_email': forms.EmailInput(attrs={
                'placeholder': 'tu.email@empresa.com'
            }),
            'available_times': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ej: Lunes a Viernes de 8:00 AM a 5:00 PM, o especifica horarios específicos...'
            }),
        }
        help_texts = {
            'description': 'Incluye todos los detalles posibles para ayudar a resolver el problema más rápido.',
            'priority': 'Selecciona la prioridad según la urgencia del problema.',
            'specific_location': 'Ayúdanos a ubicar exactamente dónde está el problema.',
            'available_times': 'Indica cuándo podemos acceder al área para realizar el mantenimiento.',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar áreas activas
        self.fields['area'].queryset = MaintenanceArea.objects.filter(
            is_active=True
        ).order_by('name')
        
        # Pre-llenar email si el usuario tiene uno
        if user and user.email and not self.instance.pk:
            self.fields['contact_email'].initial = user.email
        
        # Estilizar todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors'
            })
            
        # Estilo especial para campos obligatorios
        required_fields = ['title', 'description', 'category', 'area']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors required'
                })

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class MaintenanceReportImageForm(forms.ModelForm):
    """Formulario para subir imágenes a reportes de mantenimiento"""
    
    class Meta:
        model = MaintenanceReportImage
        fields = ['image', 'description']
        labels = {
            'image': 'Imagen',
            'description': 'Descripción de la imagen',
        }
        widgets = {
            'description': forms.TextInput(attrs={
                'placeholder': 'Describe qué se muestra en la imagen...'
            }),
            'image': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'image':  # El campo image ya tiene su clase
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
                })


class MaintenanceReportResponseForm(forms.ModelForm):
    """Formulario para que los administradores respondan a reportes"""
    
    class Meta:
        model = MaintenanceReport
        fields = ['status', 'assigned_to', 'response_to_tenant', 'internal_notes']
        labels = {
            'status': 'Estado',
            'assigned_to': 'Asignar a',
            'response_to_tenant': 'Respuesta al Inquilino',
            'internal_notes': 'Notas Internas',
        }
        widgets = {
            'response_to_tenant': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Mensaje que será visible para el inquilino...'
            }),
            'internal_notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Notas internas del equipo de mantenimiento...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar usuarios que pueden ser asignados
        self.fields['assigned_to'].queryset = User.objects.filter(
            models.Q(is_superuser=True) | 
            models.Q(groups__name__in=['Vigilantes', 'Administradores', 'Mantenimiento'])
        ).distinct().order_by('first_name', 'last_name')
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            })
