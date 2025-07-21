from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from .models import SystemThemeConfiguration


@login_required
@require_GET
def system_config_api(request):
    """API para obtener la configuración actual del sistema"""
    try:
        config = SystemThemeConfiguration.get_active_config()
        
        if config:
            data = {
                'success': True,
                'company_name': config.company_name,
                'logo_url': config.company_logo.url if config.company_logo else None,
                'colors': config.get_theme_colors(),
                'theme': config.theme,
                'dark_mode': config.dark_mode
            }
        else:
            data = {
                'success': False,
                'message': 'No se encontró configuración activa'
            }
        
        return JsonResponse(data)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
