from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard principal del admin
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    
    # Gestión de usuarios
    path('users/', views.admin_users_view, name='users'),
    
    # Configuración del sistema
    path('system/', views.admin_system_view, name='system'),
    
    # Reportes y análisis
    path('reports/', views.admin_reports_view, name='reports'),
]
