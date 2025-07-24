from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import MaintenanceReport


@receiver(pre_save, sender=MaintenanceReport)
def capture_old_status(sender, instance, **kwargs):
    """Captura el estado anterior del reporte antes de guardarlo"""
    if instance.pk:
        try:
            instance._old_status = MaintenanceReport.objects.get(pk=instance.pk).status
        except MaintenanceReport.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=MaintenanceReport)
def send_status_update_notification(sender, instance, created, **kwargs):
    """Envía notificación cuando se actualiza el estado de un reporte"""
    if not created:  # Solo para actualizaciones, no para creaciones
        old_status = getattr(instance, '_old_status', None)
        
        # Si el estado cambió
        if old_status and old_status != instance.status:
            try:
                from accounts.models import Notification
                
                # Título corto según el nuevo estado
                status_messages = {
                    'en_progreso': 'Tu reporte está en progreso',
                    'completado': 'Tu reporte fue completado',
                    'requiere_atencion': 'Tu reporte requiere atención',
                    'cancelado': 'Tu reporte fue cancelado',
                }
                
                notification_title = status_messages.get(
                    instance.status, 
                    'Tu reporte fue actualizado'
                )
                
                # Mensaje corto y directo
                simple_message = f"Estado: {instance.get_status_display()}"
                if instance.response_to_tenant:
                    simple_message += f" - {instance.response_to_tenant[:100]}{'...' if len(instance.response_to_tenant) > 100 else ''}"
                
                # Enviar notificación al inquilino que reportó
                Notification.objects.create(
                    recipient=instance.reported_by,
                    title=notification_title,
                    message=simple_message,
                    notification_type='maintenance_update',
                    maintenance_report=instance,
                    priority=2 if instance.status in ['completado', 'requiere_atencion'] else 3  # 2=Alta, 3=Media
                )
                
                print(f"✅ Notificación enviada a {instance.reported_by.username} por cambio de estado de {old_status} a {instance.status}")
                
            except Exception as e:
                print(f"❌ Error enviando notificación de actualización de reporte: {e}")


@receiver(post_save, sender=MaintenanceReport)
def send_new_report_notification(sender, instance, created, **kwargs):
    """Envía notificación a administradores cuando se crea un nuevo reporte"""
    if created:  # Solo para nuevos reportes
        try:
            from accounts.models import Notification
            
            # Obtener todos los administradores y superusuarios
            admins = User.objects.filter(
                is_superuser=True
            ).distinct()
            
            # También incluir usuarios con rol admin
            admin_role_users = User.objects.filter(
                user_role__role='admin',
                user_role__is_active=True
            ).distinct()
            
            # Combinar ambos grupos
            all_admins = admins.union(admin_role_users)
            
            # Crear el mensaje corto y directo
            reporter_name = instance.reported_by.get_full_name() or instance.reported_by.username
            
            title = f"{reporter_name} reportó problema en {instance.area.name}"
            message = f"{instance.get_category_display()} - {instance.get_priority_display()}"
            
            full_message = message
            
            # Enviar notificación a cada administrador
            for admin in all_admins:
                Notification.objects.create(
                    recipient=admin,
                    title=title,
                    message=full_message,
                    notification_type='maintenance_request',
                    maintenance_report=instance,
                    priority=2 if instance.priority <= 2 else 3  # 2=Alta, 3=Media
                )
            
            print(f"✅ Notificaciones enviadas a {all_admins.count()} administradores por nuevo reporte: {instance.title}")
            
        except Exception as e:
            print(f"❌ Error enviando notificaciones de nuevo reporte: {e}")
