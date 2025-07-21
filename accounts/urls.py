from django.urls import path
from . import views, api_views, debug_views

app_name = 'accounts'

urlpatterns = [
    # Gestión de usuarios
    path('users/', views.users_list, name='users_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/bulk-actions/', views.bulk_user_actions, name='bulk_user_actions'),
    path('assign-roles/', views.assign_roles, name='assign_roles'),
    path('assign-roles/<int:user_id>/', views.assign_user_role, name='assign_user_role'),
    
    # Notificaciones
    path('notifications/', api_views.notifications_page, name='notifications'),
    
    # Debug (solo para desarrollo)
    path('debug/user-info/', debug_views.debug_user_info, name='debug_user_info'),
]
