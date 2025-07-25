from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # API para suscripciones push
    path('api/subscribe/', views.PushSubscribeView.as_view(), name='push_subscribe'),
    path('api/unsubscribe/', views.PushUnsubscribeView.as_view(), name='push_unsubscribe'),
    
    # API para gestión de notificaciones
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_read'),
    path('api/notifications/unread-count/', views.get_unread_count, name='unread_count'),
    
    # API para preferencias
    path('api/preferences/', views.NotificationPreferencesView.as_view(), name='preferences'),
    
    # APIs de testing y administración
    path('api/test/', views.test_notification, name='test_notification'),
    path('api/emergency/', views.send_emergency_alert, name='emergency_alert'),
]
