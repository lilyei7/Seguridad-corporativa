from django import forms
from django.contrib.auth.models import User
from .models import Tenant


class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = [
            'tenant_name', 'razon_social', 'representante_legal',
            'contact_person', 'contact_email', 'contact_phone', 'telefono_oficina', 'correo_recepcion',
            'address', 'city', 'state', 'zip_code',
            'piso', 'numero_oficina', 'metros_cuadrados', 'tipo_oficina',
            'recibo_luz', 'assigned_user', 'is_active'
        ]
        widgets = {
            # Información Básica
            'tenant_name': forms.TextInput(attrs={
                'placeholder': 'Nombre del inquilino o empresa',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'razon_social': forms.TextInput(attrs={
                'placeholder': 'Razón social completa',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'representante_legal': forms.TextInput(attrs={
                'placeholder': 'Nombre del representante legal',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            
            # Información de Contacto
            'contact_person': forms.TextInput(attrs={
                'placeholder': 'Persona de contacto',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'contact_email': forms.EmailInput(attrs={
                'placeholder': 'contacto@empresa.com',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'contact_phone': forms.TextInput(attrs={
                'placeholder': '+52 555 123 4567',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'telefono_oficina': forms.TextInput(attrs={
                'placeholder': 'Teléfono de la oficina',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'correo_recepcion': forms.EmailInput(attrs={
                'placeholder': 'recepcion@empresa.com (opcional)',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            
            # Información de Ubicación
            'address': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Dirección completa del corporativo',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'city': forms.TextInput(attrs={
                'placeholder': 'Ciudad',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'state': forms.TextInput(attrs={
                'placeholder': 'Estado',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'zip_code': forms.TextInput(attrs={
                'placeholder': 'Código postal',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            
            # Información de Oficina
            'piso': forms.TextInput(attrs={
                'placeholder': 'ej: Piso 5, PB, Mezanine',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'numero_oficina': forms.TextInput(attrs={
                'placeholder': 'ej: 501, A-10, Oficina 1',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'metros_cuadrados': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'tipo_oficina': forms.Select(attrs={
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white'
            }),
            
            # Servicios
            'recibo_luz': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Información adicional sobre el recibo de luz (opcional)',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            
            # Sistema
            'assigned_user': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded text-blue-600 focus:ring-blue-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar usuarios que pueden ser asignados
        self.fields['assigned_user'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_user'].empty_label = "Seleccionar usuario (opcional)"
        
        # Hacer algunos campos opcionales
        self.fields['correo_recepcion'].required = False
        self.fields['recibo_luz'].required = False
        self.fields['assigned_user'].required = False
        
        # Labels en español
        self.fields['tenant_name'].label = "Nombre del Inquilino"
        self.fields['razon_social'].label = "Razón Social"
        self.fields['representante_legal'].label = "Representante Legal"
        self.fields['contact_person'].label = "Persona de Contacto"
        self.fields['contact_email'].label = "Email de Contacto"
        self.fields['contact_phone'].label = "Teléfono de Contacto"
        self.fields['telefono_oficina'].label = "Teléfono de Oficina"
        self.fields['correo_recepcion'].label = "Correo de Recepción"
        self.fields['address'].label = "Dirección"
        self.fields['city'].label = "Ciudad"
        self.fields['state'].label = "Estado"
        self.fields['zip_code'].label = "Código Postal"
        self.fields['piso'].label = "Piso"
        self.fields['numero_oficina'].label = "Número de Oficina"
        self.fields['metros_cuadrados'].label = "Metros Cuadrados (m²)"
        self.fields['tipo_oficina'].label = "Tipo de Oficina"
        self.fields['recibo_luz'].label = "Información del Recibo de Luz"
        self.fields['assigned_user'].label = "Usuario Asignado"
        self.fields['is_active'].label = "Activo"

    def clean_metros_cuadrados(self):
        """Validar que los metros cuadrados sean positivos"""
        metros = self.cleaned_data.get('metros_cuadrados')
        if metros is not None and metros <= 0:
            raise forms.ValidationError("Los metros cuadrados deben ser mayor a 0")
        return metros

    def clean_telefono_oficina(self):
        """Validar formato del teléfono de oficina"""
        telefono = self.cleaned_data.get('telefono_oficina')
        if telefono and len(telefono) < 10:
            raise forms.ValidationError("El teléfono debe tener al menos 10 dígitos")
        return telefono
