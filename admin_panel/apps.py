from django.apps import AppConfig


class AdminPanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_panel'
    verbose_name = 'Panel de Administración'
    
    def ready(self):
        """Configuraciones adicionales cuando la app esté lista"""
        pass
