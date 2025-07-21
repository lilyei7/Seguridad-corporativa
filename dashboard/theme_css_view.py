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

/* SIDEBAR - Aplicar tema completo */
.sidebar,
#sidebar,
.fixed.inset-y-0.left-0.z-50.w-64.bg-sidebar,
.fixed.inset-y-0.left-0.z-50.w-64 {{
    background-color: var(--theme-sidebar) !important;
}}

/* Sidebar Links */
.sidebar-link,
.sidebar a,
.sidebar .sidebar-link {{
    color: rgba(255, 255, 255, 0.8) !important;
    transition: all 0.3s ease !important;
}}

.sidebar-link:hover,
.sidebar a:hover,
.sidebar .sidebar-link:hover {{
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: white !important;
}}

.sidebar-link.active,
.sidebar a.active,
.sidebar .sidebar-link.active {{
    background-color: var(--theme-primary) !important;
    color: white !important;
}}

/* Sidebar Icons */
.sidebar-link i,
.sidebar a i,
.sidebar .fas,
.sidebar .far {{
    color: inherit !important;
}}

/* Sidebar Header/Logo */
.sidebar .logo,
.sidebar h1,
.sidebar h2,
.sidebar .brand {{
    color: white !important;
}}

/* Mobile Sidebar Overlay */
.sidebar-overlay {{
    background-color: rgba(0, 0, 0, 0.5) !important;
}}

/* Sidebar Sections */
.sidebar .section-title,
.sidebar .text-xs {{
    color: rgba(255, 255, 255, 0.6) !important;
}}

/* Botones primarios en toda la aplicación */
.btn-primary,
.bg-blue-600,
.bg-blue-500,
button.bg-blue-600,
button.bg-blue-500 {{
    background-color: var(--theme-primary) !important;
    border-color: var(--theme-primary) !important;
}}

.btn-primary:hover,
.bg-blue-700:hover,
button.bg-blue-600:hover,
button.bg-blue-500:hover {{
    background-color: var(--theme-secondary) !important;
    border-color: var(--theme-secondary) !important;
}}

/* Headers y gradientes */
.bg-gradient-to-r.from-blue-600.to-blue-700,
.admin-header {{
    background: linear-gradient(135deg, var(--theme-primary), var(--theme-secondary)) !important;
}}

/* Enlaces y texto primario */
.text-blue-600,
.text-blue-500 {{
    color: var(--theme-primary) !important;
}}

/* Bordes */
.border-blue-500,
.border-blue-600 {{
    border-color: var(--theme-primary) !important;
}}

/* Focus states */
.focus\\:ring-blue-500:focus,
.focus\\:border-blue-500:focus {{
    --tw-ring-color: var(--theme-primary) !important;
    border-color: var(--theme-primary) !important;
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

/* Mobile menu button */
.mobile-menu-button,
#mobile-menu-button {{
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
.alert-success,
.bg-green-500 {{
    background-color: var(--theme-primary) !important;
}}

/* Sidebar específico por clases comunes */
nav.sidebar,
aside.sidebar,
.navigation-sidebar {{
    background-color: var(--theme-sidebar) !important;
}}

/* Enlaces del dashboard en sidebar */
.sidebar .dashboard-link,
.sidebar .nav-link {{
    color: rgba(255, 255, 255, 0.8) !important;
    padding: 0.75rem 1rem !important;
    border-radius: 0.5rem !important;
    margin: 0.25rem 0 !important;
    display: flex !important;
    align-items: center !important;
}}

.sidebar .dashboard-link:hover,
.sidebar .nav-link:hover {{
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: white !important;
}}

.sidebar .dashboard-link.active,
.sidebar .nav-link.active {{
    background-color: var(--theme-primary) !important;
    color: white !important;
}}
"""

    return HttpResponse(css_content, content_type='text/css')
