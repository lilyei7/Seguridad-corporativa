from django.db.models.signals import post_save
from django.dispatch import receiver
from visits.models import Visit
from maintenance.models import MaintenanceReport
from .services import (
    notify_visit_approved, 
    notify_visit_rejected, 
    notify_new_visit_request,
    notify_maintenance_assigned
)
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Visit)
def handle_visit_status_change(sender, instance, created, **kwargs):
    """Maneja cambios en el estado de las visitas"""
    try:
        if created:
            # Nueva solicitud de visita - notificar a vigilantes
            notify_new_visit_request(instance)
            logger.info(f"Notificación enviada para nueva visita: {instance.id}")
        
        elif instance.status == 'aprobada':
            # Visita aprobada - notificar al inquilino
            notify_visit_approved(instance)
            logger.info(f"Notificación enviada para visita aprobada: {instance.id}")
        
        elif instance.status == 'rechazada':
            # Visita rechazada - notificar al inquilino
            notify_visit_rejected(instance)
            logger.info(f"Notificación enviada para visita rechazada: {instance.id}")
    
    except Exception as e:
        logger.error(f"Error enviando notificación para visita {instance.id}: {str(e)}")

@receiver(post_save, sender=MaintenanceReport)
def handle_maintenance_change(sender, instance, created, **kwargs):
    """Maneja cambios en reportes de mantenimiento"""
    try:
        if created and instance.tenant:
            # Nuevo reporte asignado - notificar al inquilino
            notify_maintenance_assigned(instance)
            logger.info(f"Notificación enviada para mantenimiento asignado: {instance.id}")
    
    except Exception as e:
        logger.error(f"Error enviando notificación para mantenimiento {instance.id}: {str(e)}")
