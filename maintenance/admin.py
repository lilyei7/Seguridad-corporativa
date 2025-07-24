from django.contrib import admin
from .models import (
    MaintenanceArea, MaintenanceChecklist, MaintenanceItem, 
    MaintenanceEvidence, Camera, MaintenanceReport, MaintenanceReportImage
)


@admin.register(MaintenanceArea)
class MaintenanceAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'area_type', 'floor', 'is_active', 'created_at']
    list_filter = ['area_type', 'is_active', 'floor']
    search_fields = ['name', 'location', 'description']
    ordering = ['name']


@admin.register(MaintenanceChecklist)
class MaintenanceChecklistAdmin(admin.ModelAdmin):
    list_display = ['title', 'area', 'status', 'priority', 'assigned_to', 'created_by', 'created_at']
    list_filter = ['status', 'priority', 'area', 'created_at']
    search_fields = ['title', 'description', 'notes']
    ordering = ['-created_at']
    raw_id_fields = ['assigned_to', 'created_by']


@admin.register(MaintenanceItem)
class MaintenanceItemAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'checklist', 'status', 'updated_at']
    list_filter = ['status', 'updated_at']
    search_fields = ['item_name', 'description', 'observations']
    ordering = ['-updated_at']


@admin.register(MaintenanceEvidence)
class MaintenanceEvidenceAdmin(admin.ModelAdmin):
    list_display = ['item', 'evidence_type', 'uploaded_by', 'uploaded_at']
    list_filter = ['evidence_type', 'uploaded_at']
    search_fields = ['description']
    ordering = ['-uploaded_at']


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'area', 'status', 'installation_date', 'last_maintenance']
    list_filter = ['status', 'area', 'installation_date']
    search_fields = ['name', 'location', 'model']
    ordering = ['name']


class MaintenanceReportImageInline(admin.TabularInline):
    model = MaintenanceReportImage
    extra = 0
    readonly_fields = ['uploaded_at', 'uploaded_by']


@admin.register(MaintenanceReport)
class MaintenanceReportAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'area', 'status', 'priority', 
        'reported_by', 'assigned_to', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'category', 'area', 
        'created_at', 'resolved_at'
    ]
    search_fields = [
        'title', 'description', 'specific_location', 
        'reported_by__first_name', 'reported_by__last_name'
    ]
    ordering = ['-created_at']
    raw_id_fields = ['reported_by', 'assigned_to']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MaintenanceReportImageInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'title', 'description', 'category', 'area', 
                'priority', 'specific_location'
            )
        }),
        ('Asignación', {
            'fields': ('reported_by', 'assigned_to', 'status')
        }),
        ('Contacto', {
            'fields': ('contact_phone', 'contact_email', 'available_times')
        }),
        ('Respuestas', {
            'fields': ('response_to_tenant', 'internal_notes')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MaintenanceReportImage)
class MaintenanceReportImageAdmin(admin.ModelAdmin):
    list_display = ['report', 'description', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at', 'uploaded_by']
    search_fields = ['description', 'report__title']
    ordering = ['-uploaded_at']
    readonly_fields = ['uploaded_at']
