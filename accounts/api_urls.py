from django.urls import path
from . import api_views

app_name = 'api'

urlpatterns = [
    # APIs de notificaciones
    path('notifications/', api_views.get_notifications, name='get_notifications'),
    path('notifications/<int:notification_id>/read/', api_views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', api_views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/<int:notification_id>/delete/', api_views.delete_notification, name='delete_notification'),
    path('notifications/send-bulk/', api_views.send_bulk_notification, name='send_bulk_notification'),
    path('notifications/stats/', api_views.get_notification_stats, name='notification_stats'),
]
