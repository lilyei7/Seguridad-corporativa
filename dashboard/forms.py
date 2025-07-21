from django import forms
from django.contrib.auth.models import User
from .models import SecurityIncident, SecurityCheckpoint, SystemThemeConfiguration, UserThemePreference


class SecurityIncidentForm(forms.ModelForm):
    """Formulario para reportar incidentes de seguridad"""
    
    incident_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors bg-white'
            }
        ),
        label='Fecha y Hora del Incidente'
    )
    
    class Meta:
        model = SecurityIncident
        fields = [
            'title',
            'incident_type', 
            'severity',
            'description',
            'location',
            'checkpoint',
            'incident_datetime'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors',
                'placeholder': 'Título del incidente'
            }),
            'incident_type': forms.Select(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors bg-white'
            }),
            'severity': forms.Select(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors bg-white'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors',
                'rows': 4,
                'placeholder': 'Describa detalladamente el incidente...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors',
                'placeholder': 'Ubicación específica del incidente'
            }),
            'checkpoint': forms.Select(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors bg-white'
            }),
        }
        labels = {
            'title': 'Título del Incidente',
            'incident_type': 'Tipo de Incidente',
            'severity': 'Nivel de Severidad',
            'description': 'Descripción Detallada',
            'location': 'Ubicación',
            'checkpoint': 'Punto de Seguridad (Opcional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer checkpoint opcional
        self.fields['checkpoint'].required = False
        self.fields['checkpoint'].empty_label = "Seleccionar punto de seguridad..."
        
        # Agregar clases de validación
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = True


class IncidentStatusForm(forms.ModelForm):
    """Formulario para actualizar el estado de un incidente"""
    
    class Meta:
        model = SecurityIncident
        fields = ['status', 'assigned_to', 'resolution_notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors bg-white'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors bg-white'
            }),
            'resolution_notes': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors',
                'rows': 3,
                'placeholder': 'Notas sobre la resolución del incidente...'
            }),
        }
        labels = {
            'status': 'Estado del Incidente',
            'assigned_to': 'Asignado a',
            'resolution_notes': 'Notas de Resolución',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo usuarios activos para asignación
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_to'].empty_label = "Sin asignar"
        self.fields['assigned_to'].required = False
        self.fields['resolution_notes'].required = False


class SystemThemeConfigurationForm(forms.ModelForm):
    """Formulario para configurar el tema del sistema"""
    
    class Meta:
        model = SystemThemeConfiguration
        fields = [
            'company_name', 'company_logo', 'favicon', 'theme', 'dark_mode',
            'primary_color', 'secondary_color', 'accent_color', 'sidebar_color'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Nombre de la empresa'
            }),
            'company_logo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'accept': 'image/*'
            }),
            'favicon': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'accept': 'image/*'
            }),
            'theme': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'onchange': 'previewTheme(this.value)'
            }),
            'dark_mode': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded',
                'onchange': 'toggleDarkModePreview()'
            }),
            'primary_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'h-10 w-20 border border-gray-300 rounded cursor-pointer',
                'onchange': 'updateColorPreview("primary", this.value)'
            }),
            'secondary_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'h-10 w-20 border border-gray-300 rounded cursor-pointer',
                'onchange': 'updateColorPreview("secondary", this.value)'
            }),
            'accent_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'h-10 w-20 border border-gray-300 rounded cursor-pointer',
                'onchange': 'updateColorPreview("accent", this.value)'
            }),
            'sidebar_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'h-10 w-20 border border-gray-300 rounded cursor-pointer',
                'onchange': 'updateColorPreview("sidebar", this.value)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar labels
        self.fields['company_name'].label = 'Nombre de la Empresa'
        self.fields['company_logo'].label = 'Logo de la Empresa'
        self.fields['favicon'].label = 'Favicon'
        self.fields['theme'].label = 'Tema Predefinido'
        self.fields['dark_mode'].label = 'Activar Modo Oscuro por Defecto'
        self.fields['primary_color'].label = 'Color Primario'
        self.fields['secondary_color'].label = 'Color Secundario'
        self.fields['accent_color'].label = 'Color de Acento'
        self.fields['sidebar_color'].label = 'Color del Sidebar'
        
        # Ayuda para los campos
        self.fields['company_logo'].help_text = 'Formatos recomendados: PNG, JPG. Tamaño máximo: 2MB'
        self.fields['favicon'].help_text = 'Formato recomendado: ICO, PNG. Tamaño: 16x16 o 32x32 píxeles'
        self.fields['primary_color'].help_text = 'Color principal del sistema'
        self.fields['secondary_color'].help_text = 'Color secundario para elementos de apoyo'
        self.fields['accent_color'].help_text = 'Color para resaltar elementos importantes'
        self.fields['sidebar_color'].help_text = 'Color de fondo del menú lateral'


class UserThemePreferenceForm(forms.ModelForm):
    """Formulario para preferencias de tema del usuario"""
    
    class Meta:
        model = UserThemePreference
        fields = ['dark_mode', 'preferred_theme']
        widgets = {
            'dark_mode': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded',
                'id': 'user-dark-mode-toggle'
            }),
            'preferred_theme': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'id': 'user-theme-selector'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['dark_mode'].label = 'Modo Oscuro'
        self.fields['preferred_theme'].label = 'Tema Preferido'
        
        self.fields['dark_mode'].help_text = 'Activar modo oscuro para tu cuenta'
        self.fields['preferred_theme'].help_text = 'Selecciona tu tema favorito (anula el tema del sistema)'


class QuickThemeForm(forms.Form):
    """Formulario rápido para cambio de tema"""
    
    theme = forms.ChoiceField(
        choices=SystemThemeConfiguration.THEME_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'onchange': 'quickThemeChange(this.value)'
        })
    )
    
    dark_mode = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded',
            'onchange': 'quickDarkModeToggle()'
        })
    )
