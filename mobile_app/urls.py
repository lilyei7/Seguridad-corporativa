from django.urls import path
from . import views

app_name = 'mobile_app'

urlpatterns = [
    # =====================================================
    # RUTAS MÓVILES PARA INQUILINOS
    # =====================================================
    path('inquilino-movil/', views.TenantMobileDashboard.as_view(), name='tenant_dashboard'),
    path('inquilino-movil/visitas/', views.tenant_mobile_visits, name='tenant_visits'),
    path('inquilino-movil/solicitar-visita/', views.tenant_mobile_request_visit, name='tenant_request_visit'),
    
    # =====================================================
    # RUTAS MÓVILES PARA VIGILANTES  
    # =====================================================
    path('vigilante-movil/', views.GuardMobileDashboard.as_view(), name='guard_dashboard'),
    path('vigilante-movil/scanner/', views.guard_mobile_scanner, name='guard_scanner'),
    path('vigilante-movil/visitas/', views.guard_mobile_visits, name='guard_visits'),
    
    # =====================================================
    # RUTAS MÓVILES PARA ADMINISTRADORES
    # =====================================================
    path('admin-movil/', views.AdminMobileDashboard.as_view(), name='admin_dashboard'),
    path('admin-movil/monitor/', views.admin_mobile_live_monitor, name='admin_monitor'),
    
    # =====================================================
    # API ENDPOINTS MÓVILES
    # =====================================================
    path('api/aprobar-visita/<int:visit_id>/', views.mobile_api_approve_visit, name='api_approve_visit'),
    path('api/registrar-entrada/<int:visit_id>/', views.mobile_api_register_entry, name='api_register_entry'),
]
