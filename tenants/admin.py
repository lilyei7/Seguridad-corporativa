from django.contrib import admin
from .models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['tenant_name', 'contact_person', 'contact_email', 'city', 'is_active', 'created_at']
    list_filter = ['is_active', 'city', 'state', 'created_at']
    search_fields = ['tenant_name', 'contact_person', 'contact_email']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información del Inquilino', {
            'fields': ('tenant_name', 'is_active')
        }),
        ('Información de Contacto', {
            'fields': ('contact_person', 'contact_email', 'contact_phone')
        }),
        ('Dirección', {
            'fields': ('address', 'city', 'state', 'zip_code')
        }),
        ('Asignación', {
            'fields': ('assigned_user',)
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
