from django.conf import settings
from .models import SystemThemeConfiguration, UserThemePreference


def theme_context(request):
    """Context processor para datos de tema y configuración"""
    context = {}
    
    # Obtener configuración activa del sistema
    system_config = SystemThemeConfiguration.get_active_config()
    if system_config:
        context['system_config'] = system_config
        context['system_theme_colors'] = system_config.get_theme_colors()
    
    # Si hay usuario autenticado, obtener sus preferencias
    if request.user.is_authenticated:
        try:
            user_preference = UserThemePreference.objects.get(user=request.user)
            context['user_theme_preference'] = user_preference
            
            # Si el usuario tiene tema personalizado, usarlo
            if user_preference.preferred_theme:
                temp_config = SystemThemeConfiguration(theme=user_preference.preferred_theme)
                context['active_theme_colors'] = temp_config.get_theme_colors()
            else:
                context['active_theme_colors'] = context.get('system_theme_colors', {})
                
            # Aplicar modo oscuro del usuario
            context['is_dark_mode'] = user_preference.dark_mode
            
        except UserThemePreference.DoesNotExist:
            # Crear preferencias por defecto
            if system_config:
                UserThemePreference.objects.create(
                    user=request.user,
                    dark_mode=system_config.dark_mode,
                    preferred_theme='default'
                )
            context['active_theme_colors'] = context.get('system_theme_colors', {})
            context['is_dark_mode'] = system_config.dark_mode if system_config else False
    else:
        context['active_theme_colors'] = context.get('system_theme_colors', {})
        context['is_dark_mode'] = system_config.dark_mode if system_config else False
    
    return context


def pwa_context(request):
    """Context processor para datos de PWA y notificaciones push"""
    context = {}
    
    # VAPID public key para notificaciones push
    vapid_public_key = getattr(settings, 'VAPID_PUBLIC_KEY', None)
    if vapid_public_key:
        context['vapid_public_key'] = vapid_public_key
    
    # URLs importantes para PWA
    context['pwa_urls'] = {
        'dashboard': '/dashboard/',
        'admin_mobile': '/admin-movil/',
        'guard_mobile': '/vigilante-movil/',
        'tenant_mobile': '/inquilino-movil/',
        'offline': '/offline/',
    }
    
    # Configuración PWA
    context['pwa_config'] = {
        'app_name': 'SecureCorp Admin',
        'app_short_name': 'SecureCorp',
        'theme_color': '#0ea5e9',
        'background_color': '#0ea5e9',
        'version': '1.0.0'
    }
    
    return context
