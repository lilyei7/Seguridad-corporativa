from django.apps import AppConfig


class TenantPanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tenant_panel'
    verbose_name = 'Panel de Inquilinos'
    
    def ready(self):
        """Configuraciones adicionales cuando la app esté lista"""
        pass
