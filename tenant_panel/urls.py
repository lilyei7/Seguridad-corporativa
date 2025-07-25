from django.urls import path
from . import views

app_name = 'tenant_panel'

urlpatterns = [
    # Dashboard principal del inquilino
    path('', views.TenantDashboardView.as_view(), name='dashboard'),
    
    # Gestión de visitas
    path('visits/', views.TenantVisitsView.as_view(), name='visits'),
    path('visits/create/', views.tenant_create_visit, name='create_visit'),
    path('visits/<int:visit_id>/', views.tenant_visit_detail, name='visit_detail'),
    
    # Reportes de mantenimiento
    path('maintenance/', views.tenant_maintenance_view, name='maintenance'),
    
    # Perfil del inquilino
    path('profile/', views.tenant_profile_view, name='profile'),
]
