from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json

from .models import SystemThemeConfiguration, UserThemePreference
from .forms import SystemThemeConfigurationForm, UserThemePreferenceForm


def is_admin_or_superuser(user):
    """Verifica si el usuario es admin o superuser"""
    return user.is_superuser or user.is_staff


class SystemConfigurationView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista principal de configuración del sistema"""
    model = SystemThemeConfiguration
    template_name = 'dashboard/system_configuration.html'
    context_object_name = 'configurations'
    
    def test_func(self):
        return is_admin_or_superuser(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_config = SystemThemeConfiguration.get_active_config()
        context['active_config'] = active_config
        context['theme_choices'] = SystemThemeConfiguration.THEME_CHOICES
        
        user_preference, created = UserThemePreference.objects.get_or_create(
            user=self.request.user
        )
        context['user_preference'] = user_preference
        
        return context


class CreateSystemConfigurationView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Vista para crear nueva configuración del sistema"""
    model = SystemThemeConfiguration
    form_class = SystemThemeConfigurationForm
    template_name = 'dashboard/system_configuration_form.html'
    success_url = reverse_lazy('dashboard:system_configuration')
    
    def test_func(self):
        return is_admin_or_superuser(self.request.user)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Configuración creada exitosamente.'})
        
        messages.success(self.request, 'Configuración creada exitosamente.')
        return response


class UpdateSystemConfigurationView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para actualizar configuración del sistema"""
    model = SystemThemeConfiguration
    form_class = SystemThemeConfigurationForm
    template_name = 'dashboard/system_configuration_form.html'
    success_url = reverse_lazy('dashboard:system_configuration')
    
    def test_func(self):
        return is_admin_or_superuser(self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Configuración actualizada exitosamente.'})
        
        messages.success(self.request, 'Configuración actualizada exitosamente.')
        return response


@login_required
@user_passes_test(is_admin_or_superuser)
def activate_configuration(request, pk):
    """Activa una configuración específica"""
    if request.method == 'POST':
        config = get_object_or_404(SystemThemeConfiguration, pk=pk)
        
        # Desactivar todas las configuraciones
        SystemThemeConfiguration.objects.filter(is_active=True).update(is_active=False)
        
        # Activar la seleccionada
        config.is_active = True
        config.save()
        
        messages.success(request, f'Configuración "{config.company_name}" activada exitosamente.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Configuración activada'})
    
    return redirect('dashboard:system_configuration')


@login_required
def update_user_preferences(request):
    """Actualiza las preferencias de tema del usuario"""
    user_preference, created = UserThemePreference.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        # Manejar los campos del formulario
        dark_mode = request.POST.get('dark_mode') == 'on' or request.POST.get('dark_mode') == 'true'
        preferred_theme = request.POST.get('preferred_theme', '')
        
        user_preference.dark_mode = dark_mode
        user_preference.preferred_theme = preferred_theme
        user_preference.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': 'Preferencias actualizadas',
                'dark_mode': user_preference.dark_mode,
                'theme': user_preference.preferred_theme
            })
        
        messages.success(request, 'Preferencias actualizadas exitosamente.')
        return redirect('dashboard:system_configuration')
    else:
        form = UserThemePreferenceForm(instance=user_preference)
    
    return render(request, 'dashboard/user_preferences_form.html', {
        'form': form,
        'user_preference': user_preference
    })


@login_required
def toggle_dark_mode(request):
    """Toggle del modo oscuro para el usuario actual"""
    if request.method == 'POST':
        user_preference, created = UserThemePreference.objects.get_or_create(
            user=request.user
        )
        
        user_preference.dark_mode = not user_preference.dark_mode
        user_preference.save()
        
        return JsonResponse({
            'success': True,
            'dark_mode': user_preference.dark_mode,
            'message': f'Modo {"oscuro" if user_preference.dark_mode else "claro"} activado'
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
@user_passes_test(is_admin_or_superuser)
def preview_theme(request):
    """Vista previa de un tema específico"""
    if request.method == 'POST':
        theme_name = request.POST.get('theme')
        
        # Crear configuración temporal para vista previa
        temp_config = SystemThemeConfiguration(theme=theme_name)
        theme_colors = temp_config.get_theme_colors()
        
        return JsonResponse({
            'success': True,
            'theme': theme_name,
            'colors': theme_colors
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
def get_current_theme_data(request):
    """Obtiene los datos del tema actual para aplicar en el frontend"""
    config = SystemThemeConfiguration.get_active_config()
    user_preference = getattr(request.user, 'userthemepreference', None)
    
    if config:
        theme_colors = config.get_theme_colors()
        
        # Si el usuario tiene preferencias personalizadas, usar esas
        if user_preference:
            theme_colors.update({
                'dark_mode': user_preference.dark_mode,
                'user_theme': user_preference.preferred_theme
            })
        
        return JsonResponse({
            'success': True,
            'config': {
                'company_name': config.company_name,
                'theme': config.theme,
                'dark_mode': config.dark_mode,
                'colors': theme_colors,
                'logo_url': config.company_logo.url if config.company_logo else None,
                'favicon_url': config.favicon.url if config.favicon else None,
            },
            'user_preferences': {
                'dark_mode': user_preference.dark_mode if user_preference else False,
                'preferred_theme': user_preference.preferred_theme if user_preference else 'default'
            } if user_preference else None
        })
    
    return JsonResponse({'success': False, 'message': 'No hay configuración activa'})


@login_required
@user_passes_test(is_admin_or_superuser)
def save_system_configuration(request):
    """Vista simple para guardar configuración del sistema"""
    if request.method == 'POST':
        try:
            # Crear nueva configuración
            config = SystemThemeConfiguration()
            config.company_name = request.POST.get('company_name', 'Olcha Tecnología En Seguridad')
            config.theme = request.POST.get('theme', 'default')
            config.dark_mode = request.POST.get('dark_mode') == 'true'
            config.primary_color = request.POST.get('primary_color', '#0ea5e9')
            config.secondary_color = request.POST.get('secondary_color', '#0284c7')
            config.accent_color = request.POST.get('accent_color', '#0369a1')
            config.sidebar_color = request.POST.get('sidebar_color', '#1e293b')
            config.created_by = request.user
            
            # Manejar archivos
            if 'company_logo' in request.FILES:
                config.company_logo = request.FILES['company_logo']
            if 'favicon' in request.FILES:
                config.favicon = request.FILES['favicon']
            
            config.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Configuración guardada exitosamente'})
            
            messages.success(request, 'Configuración guardada exitosamente.')
            return redirect('dashboard:system_configuration')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
            
            messages.error(request, f'Error al guardar: {str(e)}')
            return redirect('dashboard:system_configuration')
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})
