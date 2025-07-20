from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('admin/', views.admin_panel, name='admin_panel'),
    path('guard/', views.guard_panel, name='guard_panel'),
    path('guard/mobile/', views.guard_panel, {'mobile': '1'}, name='mobile_guard_panel'),
    path('tenant/', views.tenant_panel, name='tenant_panel'),
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
]
