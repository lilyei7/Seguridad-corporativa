from django.urls import path
from . import views

app_name = 'guard_panel'

urlpatterns = [
    # Dashboard principal del vigilante
    path('', views.GuardDashboardView.as_view(), name='dashboard'),
    
    # Gestión de visitas
    path('visits/', views.GuardVisitsView.as_view(), name='visits'),
    path('visits/<int:visit_id>/approve/', views.guard_approve_visit, name='approve_visit'),
    path('visits/<int:visit_id>/entry/', views.guard_register_entry, name='register_entry'),
    path('visits/<int:visit_id>/exit/', views.guard_register_exit, name='register_exit'),
    
    # Información de inquilinos
    path('tenants/', views.guard_tenants_view, name='tenants'),
    
    # Reportes del vigilante
    path('reports/', views.guard_reports_view, name='reports'),
]
