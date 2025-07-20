from django import forms
from django.contrib.auth.models import User, Group
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column
from .models import Guard, SecurityPoint, SecurityRoute, RoutePoint


class GuardForm(forms.ModelForm):
    # Campos para el usuario
    first_name = forms.CharField(
        max_length=30,
        label='Nombre',
        widget=forms.TextInput(attrs={'placeholder': 'Nombre del vigilante'})
    )
    last_name = forms.CharField(
        max_length=30, 
        label='Apellido',
        widget=forms.TextInput(attrs={'placeholder': 'Apellido del vigilante'})
    )
    username = forms.CharField(
        max_length=150,
        label='Usuario',
        widget=forms.TextInput(attrs={'placeholder': 'usuario_sistema'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'email@ejemplo.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña segura'}),
        label='Contraseña',
        required=False
    )

    class Meta:
        model = Guard
        fields = [
            'employee_id', 'position', 'phone', 'emergency_contact', 
            'emergency_phone', 'hire_date', 'status'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'placeholder': 'ID de empleado'}),
            'phone': forms.TextInput(attrs={'placeholder': '+52 555 123 4567'}),
            'emergency_contact': forms.TextInput(attrs={'placeholder': 'Nombre de contacto de emergencia'}),
            'emergency_phone': forms.TextInput(attrs={'placeholder': '+52 555 123 4567'}),
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': ''}
        
        # Si estamos editando, cargar datos del usuario
        if self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
            self.fields['password'].required = False
            self.fields['password'].help_text = 'Dejar en blanco para mantener la contraseña actual'
        else:
            self.fields['password'].required = True

        self.helper.layout = Layout(
            Fieldset(
                'Información Personal',
                Row(
                    Column('first_name', css_class='form-group col-md-6 mb-3'),
                    Column('last_name', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                Row(
                    Column('username', css_class='form-group col-md-6 mb-3'),
                    Column('email', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                'password',
            ),
            Fieldset(
                'Información Laboral',
                Row(
                    Column('employee_id', css_class='form-group col-md-6 mb-3'),
                    Column('position', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                Row(
                    Column('phone', css_class='form-group col-md-6 mb-3'),
                    Column('emergency_phone', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                'emergency_contact',
                Row(
                    Column('hire_date', css_class='form-group col-md-6 mb-3'),
                    Column('status', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
            ),
            Submit('submit', 'Guardar Vigilante', css_class='btn btn-primary btn-lg')
        )

    def clean_username(self):
        username = self.cleaned_data['username']
        if self.instance.pk:
            # Excluir el usuario actual al verificar duplicados
            if User.objects.filter(username=username).exclude(id=self.instance.user.id).exists():
                raise forms.ValidationError("Este nombre de usuario ya existe.")
        else:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("Este nombre de usuario ya existe.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.instance.pk:
            # Excluir el usuario actual al verificar duplicados
            if User.objects.filter(email=email).exclude(id=self.instance.user.id).exists():
                raise forms.ValidationError("Este email ya está registrado.")
        else:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Este email ya está registrado.")
        return email

    def save(self, commit=True):
        # Crear o actualizar el usuario
        if self.instance.pk:
            # Actualizar usuario existente
            user = self.instance.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.username = self.cleaned_data['username']
            user.email = self.cleaned_data['email']
            
            # Solo cambiar contraseña si se proporcionó una nueva
            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])
            
            if commit:
                user.save()
        else:
            # Crear nuevo usuario
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name']
            )
            
            # Agregar al grupo de Vigilantes
            vigilantes_group, created = Group.objects.get_or_create(name='Vigilantes')
            user.groups.add(vigilantes_group)

        # Guardar el guard
        guard = super().save(commit=False)
        guard.user = user
        
        if commit:
            guard.save()
            
        return guard


class SecurityPointForm(forms.ModelForm):
    class Meta:
        model = SecurityPoint
        fields = [
            'name', 'code', 'point_type', 'location', 'floor', 'description',
            'status', 'priority', 'check_frequency_minutes', 'qr_code', 'photo'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Nombre del punto de seguridad',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'code': forms.TextInput(attrs={
                'placeholder': 'ej: P001, E01, EST01',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'point_type': forms.Select(attrs={
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Ubicación detallada del punto',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'floor': forms.TextInput(attrs={
                'placeholder': 'ej: PB, Piso 1, Sótano, Azotea',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Descripción detallada del punto y qué verificar',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white'
            }),
            'priority': forms.Select(attrs={
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white'
            }),
            'check_frequency_minutes': forms.NumberInput(attrs={
                'placeholder': '60',
                'min': '1',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'qr_code': forms.TextInput(attrs={
                'placeholder': 'Código QR para verificación (opcional)',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'photo': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Labels en español
        self.fields['name'].label = "Nombre del Punto"
        self.fields['code'].label = "Código del Punto"
        self.fields['point_type'].label = "Tipo de Punto"
        self.fields['location'].label = "Ubicación Detallada"
        self.fields['floor'].label = "Piso/Nivel"
        self.fields['description'].label = "Descripción"
        self.fields['status'].label = "Estado"
        self.fields['priority'].label = "Prioridad"
        self.fields['check_frequency_minutes'].label = "Frecuencia de Revisión (minutos)"
        self.fields['qr_code'].label = "Código QR"
        self.fields['photo'].label = "Foto del Punto"

        # Opciones de prioridad
        self.fields['priority'] = forms.ChoiceField(
            choices=[
                (1, '1 - Muy Alta (Crítico)'),
                (2, '2 - Alta (Importante)'),
                (3, '3 - Media (Normal)'),
                (4, '4 - Baja (Rutina)'),
                (5, '5 - Muy Baja (Informativo)'),
            ],
            widget=forms.Select(attrs={
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white'
            })
        )

        # Campos opcionales
        self.fields['description'].required = False
        self.fields['qr_code'].required = False
        self.fields['photo'].required = False

    def clean_code(self):
        """Validar que el código sea único y tenga formato correcto"""
        code = self.cleaned_data.get('code', '').upper()
        
        # Verificar que no existe otro punto con el mismo código
        if self.instance.pk:
            existing = SecurityPoint.objects.filter(code=code).exclude(pk=self.instance.pk)
        else:
            existing = SecurityPoint.objects.filter(code=code)
            
        if existing.exists():
            raise forms.ValidationError("Ya existe un punto de seguridad con este código")
            
        return code

    def clean_check_frequency_minutes(self):
        """Validar frecuencia de revisión"""
        frequency = self.cleaned_data.get('check_frequency_minutes')
        if frequency and frequency < 1:
            raise forms.ValidationError("La frecuencia debe ser mayor a 0 minutos")
        return frequency


class SecurityRouteForm(forms.ModelForm):
    class Meta:
        model = SecurityRoute
        fields = ['name', 'code', 'description', 'status', 'estimated_duration_minutes']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Nombre de la ruta de rondín',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'code': forms.TextInput(attrs={
                'placeholder': 'ej: R001, RN01, RD01',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Descripción de la ruta y objetivos del rondín',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white'
            }),
            'estimated_duration_minutes': forms.NumberInput(attrs={
                'placeholder': '30',
                'min': '1',
                'class': 'required-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Labels en español
        self.fields['name'].label = "Nombre de la Ruta"
        self.fields['code'].label = "Código de la Ruta"
        self.fields['description'].label = "Descripción"
        self.fields['status'].label = "Estado"
        self.fields['estimated_duration_minutes'].label = "Duración Estimada (minutos)"

        # Campos opcionales
        self.fields['description'].required = False

    def clean_code(self):
        """Validar que el código sea único"""
        code = self.cleaned_data.get('code', '').upper()
        
        if self.instance.pk:
            existing = SecurityRoute.objects.filter(code=code).exclude(pk=self.instance.pk)
        else:
            existing = SecurityRoute.objects.filter(code=code)
            
        if existing.exists():
            raise forms.ValidationError("Ya existe una ruta con este código")
            
        return code


class GuardAssignmentForm(forms.ModelForm):
    """Formulario para asignar rutas y puntos a vigilantes"""
    class Meta:
        model = Guard
        fields = ['assigned_routes', 'assigned_points']
        widgets = {
            'assigned_routes': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'assigned_points': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Labels en español
        self.fields['assigned_routes'].label = "Rutas Asignadas"
        self.fields['assigned_points'].label = "Puntos Específicos Asignados"
        
        # Filtrar solo rutas y puntos activos
        self.fields['assigned_routes'].queryset = SecurityRoute.objects.filter(status='activa')
        self.fields['assigned_points'].queryset = SecurityPoint.objects.filter(status='activo')

        # Campos opcionales
        self.fields['assigned_routes'].required = False
        self.fields['assigned_points'].required = False
