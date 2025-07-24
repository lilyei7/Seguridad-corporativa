#!/usr/bin/env python
"""
Script para poblar datos de ejemplo de solicitudes de mantenimiento
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_corp.settings')
django.setup()

from django.contrib.auth.models import User
from tenants.models import Tenant
from maintenance.models import MaintenanceRequest

def create_sample_maintenance_requests():
    """Crear solicitudes de mantenimiento de ejemplo"""
    
    try:
        # Obtener usuario y tenant de ejemplo
        user = User.objects.get(username='inquilino_ejemplo')
        tenant = Tenant.objects.get(contact_person=user)
        
        print(f"✓ Usuario encontrado: {user.username}")
        print(f"✓ Inquilino encontrado: {tenant.tenant_name}")
        
    except (User.DoesNotExist, Tenant.DoesNotExist) as e:
        print(f"❌ Error: {e}")
        print("Por favor, asegúrate de que existe el usuario 'inquilino_ejemplo' y su tenant correspondiente")
        return

    # Datos de ejemplo para solicitudes de mantenimiento
    sample_requests = [
        {
            'title': 'Goteo en el baño principal',
            'category': 'plomeria',
            'description': 'Hay un goteo constante en la llave del lavamanos del baño principal. El goteo comenzó hace 3 días y está empeorando. Se escucha constantemente y está desperdiciando agua.',
            'location_details': 'Oficina 502, baño principal, lavamanos del lado derecho',
            'urgency_level': 'media',
            'status': 'pendiente',
            'created_at': timezone.now() - timedelta(hours=2),
        },
        {
            'title': 'Aire acondicionado no enfría lo suficiente',
            'category': 'aire_acondicionado',
            'description': 'El aire acondicionado de la oficina no está enfriando adecuadamente. La temperatura se mantiene alta durante todo el día, lo que afecta la productividad. Ya revisamos el filtro y parece estar limpio.',
            'location_details': 'Oficina 502, área principal, unidad de aire acondicionado central',
            'urgency_level': 'alta',
            'status': 'en_revision',
            'created_at': timezone.now() - timedelta(days=1),
        },
        {
            'title': 'Luz fluorescente parpadea constantemente',
            'category': 'electricidad',
            'description': 'Una de las luces fluorescentes del techo parpadea constantemente, lo que causa molestias y posibles problemas de vista para los empleados. El parpadeo empezó la semana pasada.',
            'location_details': 'Oficina 502, área de trabajo, tercera luz del lado izquierdo',
            'urgency_level': 'media',
            'status': 'aprobada',
            'assigned_to': User.objects.filter(is_staff=True).first(),
            'admin_notes': 'Se necesita cambiar el ballast de la luz. Material ya solicitado.',
            'scheduled_date': timezone.now() + timedelta(days=2),
            'created_at': timezone.now() - timedelta(days=3),
        },
        {
            'title': 'Cerradura de la puerta principal con problemas',
            'category': 'cerrajeria',
            'description': 'La cerradura de la puerta principal está trabándose. Tenemos dificultades para abrir y cerrar con normalidad, especialmente en las mañanas. Esto podría ser un problema de seguridad.',
            'location_details': 'Oficina 502, puerta principal de entrada',
            'urgency_level': 'urgente',
            'status': 'en_proceso',
            'assigned_to': User.objects.filter(is_staff=True).first(),
            'admin_notes': 'Técnico asignado. Se realizará cambio completo de cerradura por seguridad.',
            'scheduled_date': timezone.now() + timedelta(hours=4),
            'created_at': timezone.now() - timedelta(hours=8),
        },
        {
            'title': 'Limpieza profunda después de renovación',
            'category': 'limpieza',
            'description': 'Necesitamos una limpieza profunda después de los trabajos de pintura que se realizaron la semana pasada. Hay restos de polvo y manchas de pintura en varias superficies.',
            'location_details': 'Oficina 502, todas las áreas que fueron pintadas',
            'urgency_level': 'baja',
            'status': 'completada',
            'assigned_to': User.objects.filter(is_staff=True).first(),
            'admin_notes': 'Limpieza programada con empresa externa.',
            'resolution_notes': 'Limpieza completada satisfactoriamente. Se removieron todos los residuos de pintura y se realizó limpieza profunda de todas las superficies.',
            'completed_at': timezone.now() - timedelta(days=1),
            'created_at': timezone.now() - timedelta(days=5),
        },
        {
            'title': 'Ventana no cierra correctamente',
            'category': 'otro',
            'description': 'La ventana del lado este de la oficina no cierra completamente, lo que permite la entrada de aire y ruido exterior. El mecanismo parece estar desalineado.',
            'location_details': 'Oficina 502, ventana del lado este, segunda ventana de izquierda a derecha',
            'urgency_level': 'media',
            'status': 'pendiente',
            'created_at': timezone.now() - timedelta(hours=12),
        },
    ]

    # Crear las solicitudes
    requests_created = 0
    
    for request_data in sample_requests:
        # Separar campos especiales
        created_at = request_data.pop('created_at')
        assigned_to = request_data.pop('assigned_to', None)
        admin_notes = request_data.pop('admin_notes', '')
        resolution_notes = request_data.pop('resolution_notes', '')
        scheduled_date = request_data.pop('scheduled_date', None)
        completed_at = request_data.pop('completed_at', None)
        
        # Verificar si ya existe una solicitud similar
        existing_request = MaintenanceRequest.objects.filter(
            tenant=tenant,
            title=request_data['title']
        ).first()
        
        if not existing_request:
            # Crear la solicitud
            request_obj = MaintenanceRequest.objects.create(
                tenant=tenant,
                requested_by=user,
                **request_data
            )
            
            # Actualizar campos especiales
            request_obj.created_at = created_at
            if assigned_to:
                request_obj.assigned_to = assigned_to
            if admin_notes:
                request_obj.admin_notes = admin_notes
            if resolution_notes:
                request_obj.resolution_notes = resolution_notes
            if scheduled_date:
                request_obj.scheduled_date = scheduled_date
            if completed_at:
                request_obj.completed_at = completed_at
                
            request_obj.save()
            
            print(f"✓ Solicitud creada: {request_obj.title} (#{request_obj.id}) - {request_obj.get_status_display()}")
            requests_created += 1
        else:
            print(f"⚠️  Solicitud ya existe: {request_data['title']}")

    print(f"\n🎉 ¡Proceso completado!")
    print(f"📊 Solicitudes de mantenimiento creadas: {requests_created}")
    print(f"👤 Para inquilino: {tenant.tenant_name}")
    print(f"🏢 Oficina: {tenant.numero_oficina}")
    
    # Mostrar estadísticas
    total_requests = MaintenanceRequest.objects.filter(tenant=tenant).count()
    pending_requests = MaintenanceRequest.objects.filter(tenant=tenant, status='pendiente').count()
    in_process_requests = MaintenanceRequest.objects.filter(tenant=tenant, status__in=['en_revision', 'aprobada', 'en_proceso']).count()
    completed_requests = MaintenanceRequest.objects.filter(tenant=tenant, status='completada').count()
    
    print(f"\n📈 Estadísticas totales:")
    print(f"   • Total: {total_requests}")
    print(f"   • Pendientes: {pending_requests}")
    print(f"   • En proceso: {in_process_requests}")
    print(f"   • Completadas: {completed_requests}")

if __name__ == '__main__':
    print("🔧 Creando solicitudes de mantenimiento de ejemplo...")
    print("=" * 60)
    create_sample_maintenance_requests()
    print("=" * 60)
