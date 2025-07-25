from django.urls import path
from . import views

app_name = 'guards'

urlpatterns = [
    # Lista de vigilantes
    path('', views.guard_list, name='guard_list'),
    
    # Vigilantes
    path('create/', views.guard_create, name='guard_create'),
    path('<int:guard_id>/', views.guard_detail, name='guard_detail'),
    path('<int:guard_id>/edit/', views.guard_edit, name='guard_edit'),
    path('<int:guard_id>/toggle-status/', views.toggle_guard_status, name='toggle_guard_status'),
    
    # Puntos de Seguridad
    path('security-points/', views.security_points_list, name='security_points_list'),
    path('security-points/create/', views.security_point_create, name='security_point_create'),
    path('security-points/<int:point_id>/', views.security_point_detail, name='security_point_detail'),
    path('security-points/<int:point_id>/edit/', views.security_point_edit, name='security_point_edit'),
    path('security-points/<int:point_id>/delete/', views.security_point_delete, name='security_point_delete'),
    
    # Rutas de Seguridad
    path('security-routes/', views.security_routes_list, name='security_routes_list'),
    path('security-routes/create/', views.security_route_create, name='security_route_create'),
    path('security-routes/<int:route_id>/', views.security_route_detail, name='security_route_detail'),
    path('security-routes/<int:route_id>/edit/', views.security_route_edit, name='security_route_edit'),
    path('security-routes/<int:route_id>/edit-points/', views.security_route_edit_points, name='security_route_edit_points'),
    
    # Asignaciones
    path('assignments/', views.guard_assignments, name='guard_assignments'),
    path('assignments/<int:guard_id>/edit/', views.guard_assignment_edit, name='guard_assignment_edit'),
]
