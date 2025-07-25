from django.apps import AppConfig


class GuardPanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'guard_panel'
    verbose_name = 'Panel de Vigilantes'
    
    def ready(self):
        """Configuraciones adicionales cuando la app esté lista"""
        pass
