from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from tenants.models import Tenant
from guards.models import Guard

class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado para crear usuarios"""
    email = forms.EmailField(required=True, label='Correo Electrónico')
    first_name = forms.CharField(max_length=30, required=True, label='Nombre(s)')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido(s)')
    role = forms.ChoiceField(
        choices=[
            ('admin', 'Administrador'),
            ('vigilante', 'Vigilante'),
            ('inquilino', 'Inquilino'),
        ],
        required=True,
        label='Rol del Usuario',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Campos adicionales para inquilinos
    tenant_business_name = forms.CharField(
        max_length=200, 
        required=False, 
        label='Nombre del Negocio',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tenant_contact_person = forms.CharField(
        max_length=150, 
        required=False, 
        label='Persona de Contacto',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tenant_phone = forms.CharField(
        max_length=20, 
        required=False, 
        label='Teléfono del Negocio',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tenant_address = forms.CharField(
        max_length=200, 
        required=False, 
        label='Dirección del Negocio',
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'})
    )
    
    # Campos adicionales para vigilantes
    guard_employee_id = forms.CharField(
        max_length=20, 
        required=False, 
        label='ID de Empleado',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    guard_phone = forms.CharField(
        max_length=20, 
        required=False, 
        label='Teléfono',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        labels = {
            'username': 'Nombre de Usuario',
            'password1': 'Contraseña',
            'password2': 'Confirmar Contraseña',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            })

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este correo electrónico.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        # Validar campos específicos según el rol
        if role == 'inquilino':
            if not cleaned_data.get('tenant_business_name'):
                raise forms.ValidationError("El nombre del negocio es requerido para inquilinos.")
        
        elif role == 'vigilante':
            if not cleaned_data.get('guard_employee_id'):
                raise forms.ValidationError("El ID de empleado es requerido para vigilantes.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Asignar rol/grupo
            role = self.cleaned_data['role']
            if role == 'admin':
                user.is_staff = True
                user.is_superuser = True
                user.save()
            elif role == 'vigilante':
                group, created = Group.objects.get_or_create(name='Vigilantes')
                user.groups.add(group)
                
                # Crear perfil de vigilante
                from datetime import date
                Guard.objects.create(
                    user=user,
                    employee_id=self.cleaned_data.get('guard_employee_id', ''),
                    phone=self.cleaned_data.get('guard_phone', ''),
                    emergency_contact='',
                    emergency_phone='',
                    hire_date=date.today(),
                    status='activo'
                )
            elif role == 'inquilino':
                group, created = Group.objects.get_or_create(name='Inquilinos')
                user.groups.add(group)
                
                # Crear perfil de inquilino
                Tenant.objects.create(
                    assigned_user=user,
                    tenant_name=self.cleaned_data.get('tenant_business_name', ''),
                    contact_person=self.cleaned_data.get('tenant_contact_person', ''),
                    contact_phone=self.cleaned_data.get('tenant_phone', ''),
                    contact_email=user.email,
                    address=self.cleaned_data.get('tenant_address', ''),
                    city='',
                    state='',
                    zip_code='',
                    is_active=True
                )
        
        return user


class UserEditForm(forms.ModelForm):
    """Formulario para editar usuarios existentes"""
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Grupos'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'groups')
        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo Electrónico',
            'first_name': 'Nombre(s)',
            'last_name': 'Apellido(s)',
            'is_active': 'Usuario Activo',
            'is_staff': 'Personal del Sitio',
            'is_superuser': 'Superusuario',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            if field_name != 'groups':  # Los checkboxes no necesitan la clase form-control
                field.widget.attrs.update({'class': 'form-control'})


class TenantEditForm(forms.ModelForm):
    """Formulario para editar información de inquilinos"""
    class Meta:
        model = Tenant
        fields = ('tenant_name', 'razon_social', 'contact_person', 'contact_email', 'contact_phone', 'address', 'city', 'state', 'zip_code', 'is_active')
        labels = {
            'tenant_name': 'Nombre del Inquilino',
            'razon_social': 'Razón Social',
            'contact_person': 'Persona de Contacto',
            'contact_email': 'Email de Contacto',
            'contact_phone': 'Teléfono de Contacto',
            'address': 'Dirección',
            'city': 'Ciudad',
            'state': 'Estado',
            'zip_code': 'Código Postal',
            'is_active': 'Activo',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.update({'class': 'form-control'})


class GuardEditForm(forms.ModelForm):
    """Formulario para editar información de vigilantes"""
    class Meta:
        model = Guard
        fields = ('employee_id', 'position', 'phone', 'emergency_contact', 'emergency_phone', 'status')
        labels = {
            'employee_id': 'ID de Empleado',
            'position': 'Puesto',
            'phone': 'Teléfono',
            'emergency_contact': 'Contacto de Emergencia',
            'emergency_phone': 'Teléfono de Emergencia',
            'status': 'Estado',
        }
        widgets = {
            'position': forms.Select(choices=[
                ('vigilante', 'Vigilante'),
                ('supervisor', 'Supervisor'),
                ('jefe_seguridad', 'Jefe de Seguridad'),
            ]),
            'status': forms.Select(choices=[
                ('activo', 'Activo'),
                ('inactivo', 'Inactivo'),
                ('suspendido', 'Suspendido'),
                ('vacaciones', 'Vacaciones'),
            ]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.update({'class': 'form-control'})


class RoleAssignmentForm(forms.Form):
    """Formulario para asignar roles a usuarios"""
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='Usuario',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Roles'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar la representación de usuarios
        self.fields['user'].queryset = User.objects.all().order_by('first_name', 'last_name', 'username')
