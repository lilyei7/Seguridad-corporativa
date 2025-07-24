from django.urls import path
from . import views, api_views, debug_views, api_notification_views

app_name = 'accounts'

urlpatterns = [
    # Autenticación
    path('logout/', views.logout_view, name='logout'),
    
    # Perfil de usuario
    path('profile/', views.user_profile, name='profile'),
    
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
    
    # Notificaciones - Páginas
    path('notifications/', api_views.notifications_page, name='notifications'),
    
    # Notificaciones - API
    path('api/notifications/', api_notification_views.notifications_api, name='notifications_api'),
    path('api/notifications/counts/', api_notification_views.notification_counts, name='notification_counts'),
    path('api/notifications/recent/', api_notification_views.recent_notifications, name='recent_notifications'),
    path('api/notifications/<int:notification_id>/read/', api_notification_views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/<int:notification_id>/dismiss/', api_notification_views.dismiss_notification, name='dismiss_notification'),
    path('api/notifications/mark-all-read/', api_notification_views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/notifications/test/', api_notification_views.send_test_notification, name='send_test_notification'),
    
    # Debug (solo para desarrollo)
    path('debug/user-info/', debug_views.debug_user_info, name='debug_user_info'),
]
