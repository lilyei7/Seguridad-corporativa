from django.contrib import admin
from .models import Visit, VisitLog


class VisitLogInline(admin.TabularInline):
    model = VisitLog
    extra = 0
    readonly_fields = ['timestamp']


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = [
        'visitor_name', 'tenant', 'scheduled_date', 'scheduled_time', 
        'status', 'visit_type', 'registered_by'
    ]
    list_filter = ['status', 'visit_type', 'scheduled_date', 'tenant']
    search_fields = ['visitor_name', 'visitor_company', 'tenant__tenant_name']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at', 'is_overdue']
    date_hierarchy = 'scheduled_date'
    inlines = [VisitLogInline]
    
    fieldsets = (
        ('Información del Visitante', {
            'fields': ('visitor_name', 'visitor_email', 'visitor_phone', 
                      'visitor_company', 'visitor_id_number')
        }),
        ('Información de la Visita', {
            'fields': ('tenant', 'visit_type', 'purpose', 'authorized_by')
        }),
        ('Programación', {
            'fields': ('scheduled_date', 'scheduled_time')
        }),
        ('Control de Acceso', {
            'fields': ('status', 'actual_arrival_time', 'actual_departure_time',
                      'registered_by', 'approved_by')
        }),
        ('Información Adicional', {
            'fields': ('vehicle_plates', 'items_brought', 'items_taken', 'notes')
        }),
        ('Estado del Sistema', {
            'fields': ('is_overdue', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VisitLog)
class VisitLogAdmin(admin.ModelAdmin):
    list_display = ['visit', 'action', 'performed_by', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['visit__visitor_name', 'performed_by__user__username']
    readonly_fields = ['timestamp']
