from django.core.management.base import BaseCommand
from notifications.models import NotificationTemplate

class Command(BaseCommand):
    help = 'Crea templates de notificaciones por defecto'

    def handle(self, *args, **options):
        templates = [
            {
                'notification_type': 'visit_approved',
                'title_template': '✅ Visita Aprobada',
                'body_template': 'Tu visita de {visitor_name} para el {date} a las {time} ha sido aprobada.',
                'icon_url': '/static/img/visit-approved.png',
                'action_url': '/inquilino-movil/'
            },
            {
                'notification_type': 'visit_rejected',
                'title_template': '❌ Visita Rechazada',
                'body_template': 'Tu visita de {visitor_name} para el {date} a las {time} ha sido rechazada.',
                'icon_url': '/static/img/visit-rejected.png',
                'action_url': '/inquilino-movil/'
            },
            {
                'notification_type': 'visit_arrived',
                'title_template': '🚪 Visitante Llegó',
                'body_template': '{visitor_name} ha llegado a las {time}. Te esperan en recepción.',
                'icon_url': '/static/img/visitor-arrived.png',
                'action_url': '/inquilino-movil/'
            },
            {
                'notification_type': 'visit_request',
                'title_template': '📋 Nueva Solicitud de Visita',
                'body_template': '{tenant_name} (Unidad {unit}) solicita visita de {visitor_name} para {date} {time}.',
                'icon_url': '/static/img/visit-request.png',
                'action_url': '/vigilante-movil/visitas/'
            },
            {
                'notification_type': 'maintenance_assigned',
                'title_template': '🔧 Mantenimiento Asignado',
                'body_template': 'Se ha asignado mantenimiento: {title}. Prioridad: {priority}.',
                'icon_url': '/static/img/maintenance.png',
                'action_url': '/inquilino-movil/'
            },
            {
                'notification_type': 'emergency_alert',
                'title_template': '🚨 ALERTA DE EMERGENCIA',
                'body_template': '{message} - {timestamp}',
                'icon_url': '/static/img/emergency.png',
                'action_url': '/admin-movil/'
            },
            {
                'notification_type': 'general_announcement',
                'title_template': '📢 Anuncio Importante',
                'body_template': '{message}',
                'icon_url': '/static/img/announcement.png',
                'action_url': '/inquilino-movil/'
            },
        ]

        created_count = 0
        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                notification_type=template_data['notification_type'],
                defaults=template_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Template creado: {template.notification_type}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Template ya existe: {template.notification_type}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Proceso completado. {created_count} templates nuevos creados.')
        )
