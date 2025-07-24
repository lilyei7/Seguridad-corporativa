from django.urls import path
from . import api_views
from . import api_notifications

app_name = 'api'

urlpatterns = [
    # APIs de notificaciones (nuevas optimizadas)
    path('notifications/list/', api_notifications.get_notifications_api, name='get_notifications_new'),
    path('notifications/<int:notification_id>/read/', api_notifications.mark_notification_read_api, name='mark_notification_read_new'),
    path('notifications/mark-all-read/', api_notifications.mark_all_notifications_read_api, name='mark_all_notifications_read_new'),
    
    # APIs de notificaciones (legacy)
    path('notifications/', api_views.get_notifications, name='get_notifications'),
    path('notifications/<int:notification_id>/read/', api_views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', api_views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/<int:notification_id>/delete/', api_views.delete_notification, name='delete_notification'),
    path('notifications/send-bulk/', api_views.send_bulk_notification, name='send_bulk_notification'),
    path('notifications/stats/', api_views.get_notification_stats, name='notification_stats'),
]
