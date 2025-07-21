from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import SystemThemeConfiguration, UserThemePreference


def theme_css(request):
    """Genera CSS dinámico basado en la configuración de tema activa"""
    
    # Obtener configuración activa
    config = SystemThemeConfiguration.get_active_config()
    
    # Si hay usuario autenticado, verificar sus preferencias
    user_colors = None
    if request.user.is_authenticated:
        try:
            user_preference = UserThemePreference.objects.get(user=request.user)
            if user_preference.preferred_theme:
                # Usuario tiene tema personalizado
                temp_config = SystemThemeConfiguration(theme=user_preference.preferred_theme)
                user_colors = temp_config.get_theme_colors()
        except UserThemePreference.DoesNotExist:
            pass
    
    # Usar colores del usuario o del sistema
    if user_colors:
        colors = user_colors
    elif config:
        colors = config.get_theme_colors()
    else:
        # Colores por defecto si no hay configuración
        colors = {
            'primary': '#0ea5e9',
            'secondary': '#0284c7',
            'accent': '#0369a1',
            'sidebar': '#1e293b'
        }
    
    # Generar CSS dinámico
    css_content = f"""
/* CSS Dinámico - Tema del Sistema */

:root {{
    --theme-primary: {colors['primary']};
    --theme-secondary: {colors['secondary']};
    --theme-accent: {colors['accent']};
    --theme-sidebar: {colors['sidebar']};
}}

/* Sidebar */
.sidebar {{
    background-color: var(--theme-sidebar) !important;
}}

.sidebar-link.active,
.sidebar-link:hover {{
    background-color: rgba(255, 255, 255, 0.1) !important;
}}

/* Botones primarios */
.btn-primary,
.bg-blue-600,
.bg-blue-500 {{
    background-color: var(--theme-primary) !important;
}}

.btn-primary:hover,
.bg-blue-700:hover {{
    background-color: var(--theme-secondary) !important;
}}

/* Headers y gradientes */
.bg-gradient-to-r.from-blue-600.to-blue-700 {{
    background: linear-gradient(135deg, var(--theme-primary), var(--theme-secondary)) !important;
}}

/* Enlaces y texto primario */
.text-blue-600 {{
    color: var(--theme-primary) !important;
}}

.text-blue-500 {{
    color: var(--theme-primary) !important;
}}

/* Bordes */
.border-blue-500 {{
    border-color: var(--theme-primary) !important;
}}

.border-blue-600 {{
    border-color: var(--theme-secondary) !important;
}}

/* Focus states */
.focus\\:ring-blue-500:focus {{
    --tw-ring-color: var(--theme-primary) !important;
}}

.focus\\:border-blue-500:focus {{
    border-color: var(--theme-primary) !important;
}}

/* Iconos con color de tema */
.text-blue-600 i,
.text-blue-500 i {{
    color: inherit !important;
}}

/* Backgrounds de tema */
.bg-blue-100 {{
    background-color: color-mix(in srgb, var(--theme-primary) 10%, white) !important;
}}

.bg-blue-50 {{
    background-color: color-mix(in srgb, var(--theme-primary) 5%, white) !important;
}}

/* Estados hover para cards */
.hover\\:bg-blue-50:hover {{
    background-color: color-mix(in srgb, var(--theme-primary) 5%, white) !important;
}}

/* Aplicar a elementos específicos del dashboard */
.admin-header {{
    background: linear-gradient(135deg, var(--theme-primary), var(--theme-secondary)) !important;
}}

/* Mobile menu */
.mobile-menu-button {{
    color: var(--theme-primary) !important;
}}

/* Theme cards en configuración */
.theme-card.selected {{
    border-color: var(--theme-primary) !important;
    background-color: color-mix(in srgb, var(--theme-primary) 5%, white) !important;
}}

/* Botones de configuración */
.config-save-btn {{
    background-color: var(--theme-primary) !important;
}}

.config-save-btn:hover {{
    background-color: var(--theme-secondary) !important;
}}

/* Alertas de éxito */
.alert-success {{
    background-color: var(--theme-primary) !important;
}}
"""

    return HttpResponse(css_content, content_type='text/css')
