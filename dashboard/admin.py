from django.contrib import admin
from .models import SecurityCheckpoint, SecurityIncident, SystemConfiguration


@admin.register(SecurityCheckpoint)
class SecurityCheckpointAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'location']
    list_editable = ['is_active']


@admin.register(SecurityIncident)
class SecurityIncidentAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'incident_type', 'severity', 'status', 
        'reported_by', 'incident_datetime'
    ]
    list_filter = ['incident_type', 'severity', 'status', 'incident_datetime']
    search_fields = ['title', 'description', 'location']
    list_editable = ['status', 'severity']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'incident_datetime'
    
    fieldsets = (
        ('Información del Incidente', {
            'fields': ('title', 'incident_type', 'severity', 'status')
        }),
        ('Detalles', {
            'fields': ('description', 'location', 'checkpoint', 'incident_datetime')
        }),
        ('Asignación', {
            'fields': ('reported_by', 'assigned_to')
        }),
        ('Resolución', {
            'fields': ('resolution_notes', 'resolved_at')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ['key', 'description', 'updated_by', 'updated_at']
    search_fields = ['key', 'description']
    readonly_fields = ['updated_at']
