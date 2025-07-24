"""
URLs para la API de notificaciones de mantenimiento
"""
from django.urls import path
from . import api_views

app_name = 'maintenance_api'

urlpatterns = [
    path('notifications/', api_views.get_maintenance_notifications, name='get_notifications'),
    path('notifications/create/', api_views.create_maintenance_notification, name='create_notification'),
    path('stats/', api_views.get_maintenance_stats, name='get_stats'),
]
