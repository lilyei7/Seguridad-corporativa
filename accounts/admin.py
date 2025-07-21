from django.contrib import admin
from .models import UserRole, Notification, UserPreferences

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering = ['-created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'priority', 'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'read_at']

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'dashboard_layout', 'email_notifications', 'push_notifications', 'updated_at']
    list_filter = ['dashboard_layout', 'email_notifications', 'push_notifications']
    search_fields = ['user__username', 'user__email']
    ordering = ['-updated_at']
