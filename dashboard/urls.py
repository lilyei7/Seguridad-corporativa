from django.urls import path
from . import views, config_views, api_views
from .theme_css_view import theme_css

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('admin/', views.admin_panel, name='admin_panel'),
    path('guard/', views.guard_panel, name='guard_panel'),
    path('guard/mobile/', views.guard_panel, {'mobile': '1'}, name='mobile_guard_panel'),
    path('tenant/', views.tenant_panel, name='tenant_panel'),
    path('tenant/dashboard/', views.tenant_panel, name='tenant_dashboard'),
    path('visits/', views.visits_list, name='visits_list'),
    path('tenants/', views.tenants_list, name='tenants_list'),
    path('guards/', views.guards_list, name='guards_list'),
    path('visit/<int:visit_id>/', views.visit_detail, name='visit_detail'),
    path('visit/<int:visit_id>/arrived/', views.mark_visit_arrived, name='mark_visit_arrived'),
    path('visit/<int:visit_id>/departed/', views.mark_visit_departed, name='mark_visit_departed'),
    # URLs para incidentes de seguridad
    path('incidents/', views.incidents_list, name='incidents_list'),
    path('incidents/create/', views.incident_create, name='incident_create'),
    path('incidents/<int:incident_id>/', views.incident_detail, name='incident_detail'),
    path('incidents/<int:incident_id>/edit/', views.incident_edit, name='incident_edit'),
    # URLs adicionales faltantes
    path('my-shift/', views.my_shift, name='my_shift'),
    
    # API endpoints
    path('api/system-config/', api_views.system_config_api, name='system_config_api'),
    
    # URLs para configuración del sistema
    path('config/', config_views.SystemConfigurationView.as_view(), name='system_configuration'),
    path('config/create/', config_views.CreateSystemConfigurationView.as_view(), name='create_system_configuration'),
    path('config/save/', config_views.save_system_configuration, name='save_system_configuration'),
    path('config/<int:pk>/edit/', config_views.UpdateSystemConfigurationView.as_view(), name='edit_system_configuration'),
    path('config/<int:pk>/activate/', config_views.activate_configuration, name='activate_configuration'),
    path('config/preview-theme/', config_views.preview_theme, name='preview_theme'),
    path('config/theme-data/', config_views.get_current_theme_data, name='get_current_theme_data'),
    
    # URLs para preferencias de usuario
    path('preferences/', config_views.update_user_preferences, name='user_preferences'),
    path('preferences/toggle-dark-mode/', config_views.toggle_dark_mode, name='toggle_dark_mode'),
    
    # CSS dinámico para temas
    path('theme.css', theme_css, name='theme_css'),
]
