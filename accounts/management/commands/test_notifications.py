from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserRole, Notification

class Command(BaseCommand):
    help = 'Prueba el sistema de notificaciones'

    def handle(self, *args, **options):
        # Obtener usuario admin
        try:
            admin_user = User.objects.filter(
                role_profile__role='admin', 
                role_profile__is_active=True
            ).first()
            
            if not admin_user:
                self.stdout.write(
                    self.style.ERROR('No se encontró ningún usuario administrador activo')
                )
                return
            
            # Crear notificación de prueba
            notification = Notification.objects.create(
                recipient=admin_user,
                title='Prueba del Sistema de Notificaciones',
                message='Esta es una notificación de prueba para verificar que el sistema funciona correctamente.',
                notification_type='system_alert',
                priority='medium'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Notificación creada exitosamente para {admin_user.username}')
            )
            
            # Verificar que se puede consultar
            notifications = Notification.objects.filter(
                recipient=admin_user,
                is_dismissed=False
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'📧 Total de notificaciones activas: {notifications.count()}')
            )
            
            # Mostrar las notificaciones
            for notif in notifications[:5]:  # Mostrar las primeras 5
                self.stdout.write(f'  - {notif.title} ({notif.get_priority_display()})')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            )
