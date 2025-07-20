from django.contrib import admin
from .models import Guard, Shift


@admin.register(Guard)
class GuardAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'employee_id', 'position', 'status', 'phone', 'hire_date']
    list_filter = ['status', 'position', 'hire_date']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'phone']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('user', 'photo')
        }),
        ('Información Laboral', {
            'fields': ('employee_id', 'position', 'status', 'hire_date')
        }),
        ('Información de Contacto', {
            'fields': ('phone', 'emergency_contact', 'emergency_phone')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['guard', 'shift_type', 'date', 'start_time', 'end_time']
    list_filter = ['shift_type', 'date', 'guard__status']
    search_fields = ['guard__user__first_name', 'guard__user__last_name', 'guard__employee_id']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Información del Turno', {
            'fields': ('guard', 'shift_type', 'date')
        }),
        ('Horarios', {
            'fields': ('start_time', 'end_time')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
    )
