from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.services import PushNotificationService

User = get_user_model()

class Command(BaseCommand):
    help = 'Envía una notificación de prueba'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Usuario al que enviar la notificación')
        parser.add_argument('--title', type=str, default='Notificación de Prueba', help='Título de la notificación')
        parser.add_argument('--message', type=str, default='Esta es una notificación de prueba del sistema.', help='Mensaje de la notificación')
        parser.add_argument('--type', type=str, default='general_announcement', help='Tipo de notificación')

    def handle(self, *args, **options):
        username = options.get('username')
        title = options['title']
        message = options['message']
        notification_type = options['type']

        try:
            if username:
                # Enviar a usuario específico
                try:
                    user = User.objects.get(username=username)
                    service = PushNotificationService()
                    
                    success = service.send_notification_to_user(
                        user=user,
                        notification_type=notification_type,
                        title=title,
                        message=message
                    )
                    
                    if success:
                        self.stdout.write(
                            self.style.SUCCESS(f'Notificación enviada correctamente a {username}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'No se pudo enviar la notificación a {username} (usuario sin suscripciones push)')
                        )
                        
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Usuario {username} no encontrado')
                    )
            else:
                # Enviar a todos los usuarios con suscripciones activas
                service = PushNotificationService()
                sent_count = service.broadcast_notification(
                    notification_type=notification_type,
                    title=title,
                    message=message
                )
                
                if sent_count > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'Notificación enviada a {sent_count} usuarios')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('No hay usuarios con suscripciones push activas')
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error enviando notificación: {str(e)}')
            )

        # Mostrar estadísticas
        self.show_subscription_stats()

    def show_subscription_stats(self):
        from notifications.models import PushSubscription
        
        total_users = User.objects.count()
        total_subscriptions = PushSubscription.objects.filter(is_active=True).count()
        users_with_subscriptions = PushSubscription.objects.filter(is_active=True).values('user').distinct().count()
        
        self.stdout.write('')
        self.stdout.write('📊 Estadísticas de Notificaciones:')
        self.stdout.write(f'   Total de usuarios: {total_users}')
        self.stdout.write(f'   Usuarios con notificaciones activas: {users_with_subscriptions}')
        self.stdout.write(f'   Total de suscripciones activas: {total_subscriptions}')
        self.stdout.write('')
        
        if total_users > 0:
            coverage = (users_with_subscriptions / total_users) * 100
            self.stdout.write(f'   Cobertura de notificaciones: {coverage:.1f}%')
            
            if coverage < 50:
                self.stdout.write(
                    self.style.WARNING('   ⚠️  Baja cobertura de notificaciones push')
                )
            elif coverage > 80:
                self.stdout.write(
                    self.style.SUCCESS('   ✅ Excelente cobertura de notificaciones push')
                )
        
        # Ejemplos de uso
        self.stdout.write('')
        self.stdout.write('💡 Ejemplos de uso:')
        self.stdout.write('   python manage.py test_notification --username admin')
        self.stdout.write('   python manage.py test_notification --title "Emergencia" --message "Evacuación inmediata" --type emergency_alert')
        self.stdout.write('   python manage.py test_notification  # Envía a todos los usuarios')
