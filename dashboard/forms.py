from django import forms
from django.contrib.auth.models import User
from .models import SecurityIncident, SecurityCheckpoint


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
