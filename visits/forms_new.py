from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Visit
from tenants.models import Tenant


class VisitForm(forms.ModelForm):
    # Campo para la foto de identificación
    id_photo = forms.ImageField(
        required=True,
        label='Foto de Identificación',
        help_text='Tome una foto de la identificación del visitante',
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'capture': 'environment',  # Usar cámara trasera
            'class': 'hidden',
            'id': 'id_photo_input',
            'onchange': 'handlePhotoCapture(this)'
        })
    )
    
    class Meta:
        model = Visit
        fields = [
            'visitor_name', 'visitor_id_number', 'tenant', 'visit_type', 
            'purpose', 'scheduled_date', 'scheduled_time', 'authorized_by', 'notes'
        ]
        widgets = {
            'visitor_name': forms.TextInput(attrs={
                'placeholder': 'Nombre completo del visitante',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'visitor_id_number': forms.TextInput(attrs={
                'placeholder': 'Número de identificación (INE, Pasaporte, etc.)',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'tenant': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white'
            }),
            'visit_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white'
            }),
            'purpose': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Motivo de la visita',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'scheduled_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'scheduled_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'authorized_by': forms.TextInput(attrs={
                'placeholder': 'Persona que autoriza la visita',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 2, 
                'placeholder': 'Notas adicionales (opcional)',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
        }
        labels = {
            'visitor_name': 'Nombre del Visitante',
            'visitor_id_number': 'Número de Identificación',
            'tenant': 'Inquilino a Visitar',
            'visit_type': 'Tipo de Visita',
            'purpose': 'Motivo de la Visita',
            'scheduled_date': 'Fecha de Visita',
            'scheduled_time': 'Hora de Visita',
            'authorized_by': 'Autorizado por',
            'notes': 'Notas Adicionales',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar solo inquilinos activos
        self.fields['tenant'].queryset = Tenant.objects.filter(is_active=True)
        self.fields['tenant'].empty_label = "Seleccionar inquilino a visitar"
        
        # Establecer fecha y hora por defecto
        now = timezone.now()
        self.fields['scheduled_date'].initial = now.date()
        self.fields['scheduled_time'].initial = (now + timedelta(hours=1)).time().replace(second=0, microsecond=0)
        
        # Establecer fecha mínima como hoy
        self.fields['scheduled_date'].widget.attrs['min'] = now.date().strftime('%Y-%m-%d')
        
        # Hacer campos opcionales
        self.fields['notes'].required = False
        self.fields['authorized_by'].required = False

    def clean_scheduled_date(self):
        date = self.cleaned_data['scheduled_date']
        if date < timezone.now().date():
            raise forms.ValidationError("La fecha no puede ser anterior a hoy.")
        return date

    def clean_scheduled_time(self):
        time = self.cleaned_data['scheduled_time']
        date = self.cleaned_data.get('scheduled_date')
        
        if date and date == timezone.now().date():
            # Si es hoy, verificar que la hora no sea en el pasado
            now_time = timezone.now().time()
            if time < now_time:
                raise forms.ValidationError("La hora no puede ser anterior a la hora actual.")
        
        return time
