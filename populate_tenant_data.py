#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de ejemplo para el sistema de inquilinos
"""
import os
import sys
import django
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_corp.settings')
django.setup()

from tenants.models import (
    Tenant, TenantAnnouncement, MaintenanceExpense, 
    ElectricityBill, TenantIncident, TenantAccess
)
from django.contrib.auth.models import User

def create_sample_data():
    """Crear datos de ejemplo para el sistema de inquilinos"""
    
    print("Creando datos de ejemplo...")
    
    # Buscar o crear un inquilino de ejemplo
    tenant, created = Tenant.objects.get_or_create(
        tenant_name="Empresa Ejemplo S.A.",
        defaults={
            'razon_social': 'Empresa Ejemplo Sociedad Anónima',
            'representante_legal': 'Juan Pérez García',
            'contact_person': 'María González',
            'contact_email': 'contacto@empresaejemplo.com',
            'contact_phone': '+52 55 1234-5678',
            'telefono_oficina': '+52 55 8765-4321',
            'correo_recepcion': 'recepcion@empresaejemplo.com',
            'address': 'Av. Reforma 123, Col. Centro',
            'city': 'Ciudad de México',
            'state': 'CDMX',
            'zip_code': '06000',
            'piso': '5',
            'numero_oficina': '502',
            'metros_cuadrados': Decimal('85.50'),
            'tipo_oficina': 'privada',
        }
    )
    
    if created:
        print(f"✓ Inquilino creado: {tenant.tenant_name}")
    else:
        print(f"✓ Inquilino encontrado: {tenant.tenant_name}")
    
    # Buscar o crear usuario de ejemplo
    user, created = User.objects.get_or_create(
        username='inquilino_ejemplo',
        defaults={
            'email': 'inquilino@empresaejemplo.com',
            'first_name': 'María',
            'last_name': 'González',
            'is_active': True,
        }
    )
    
    if created:
        user.set_password('ejemplo123')
        user.save()
        print(f"✓ Usuario creado: {user.username}")
    else:
        print(f"✓ Usuario encontrado: {user.username}")
    
    # Crear avisos de ejemplo
    announcements_data = [
        {
            'title': 'Mantenimiento Programado del Elevador',
            'content': 'Se realizará mantenimiento preventivo del elevador principal el próximo sábado de 8:00 AM a 2:00 PM. Durante este tiempo, el elevador no estará disponible.',
            'priority': 'alta',
            'is_general': False,
        },
        {
            'title': 'Nueva Política de Visitantes',
            'content': 'A partir del próximo lunes, todos los visitantes deben registrarse en recepción y portar una identificación visible durante su estancia.',
            'priority': 'media',
            'is_general': True,
        },
        {
            'title': 'Actualización del Sistema de Seguridad',
            'content': 'El sistema de seguridad ha sido actualizado con nuevas funcionalidades. Pueden consultar las mejoras en el manual adjunto.',
            'priority': 'baja',
            'is_general': True,
        }
    ]
    
    for ann_data in announcements_data:
        announcement, created = TenantAnnouncement.objects.get_or_create(
            title=ann_data['title'],
            tenant=tenant if not ann_data['is_general'] else None,
            defaults={
                'content': ann_data['content'],
                'priority': ann_data['priority'],
                'is_general': ann_data['is_general'],
                'expires_at': timezone.now() + timedelta(days=30),
            }
        )
        if created:
            print(f"✓ Aviso creado: {announcement.title}")
    
    # Crear gastos de mantenimiento de ejemplo
    expenses_data = [
        {
            'category': 'limpieza',
            'description': 'Limpieza profunda de oficina y cristales',
            'amount': Decimal('1200.00'),
            'service_date': date.today() - timedelta(days=15),
            'provider': 'Limpieza Profesional SA',
            'invoice_number': 'LIM-2024-001',
        },
        {
            'category': 'electricidad',
            'description': 'Reparación de contactos defectuosos',
            'amount': Decimal('850.00'),
            'service_date': date.today() - timedelta(days=8),
            'provider': 'Electricidad y Más',
            'invoice_number': 'ELEC-2024-015',
        },
        {
            'category': 'aire_acondicionado',
            'description': 'Mantenimiento preventivo de sistema de climatización',
            'amount': Decimal('2400.00'),
            'service_date': date.today() - timedelta(days=3),
            'provider': 'Clima Control Empresarial',
            'invoice_number': 'CC-2024-089',
        }
    ]
    
    for exp_data in expenses_data:
        expense, created = MaintenanceExpense.objects.get_or_create(
            tenant=tenant,
            service_date=exp_data['service_date'],
            category=exp_data['category'],
            defaults=exp_data
        )
        if created:
            print(f"✓ Gasto creado: {expense.category} - ${expense.amount}")
    
    # Crear recibos de luz de ejemplo
    for i in range(6):
        bill_date = date.today().replace(day=1) - timedelta(days=30*i)
        kwh_base = 450 + (i * 25)  # Consumo variable
        amount_base = kwh_base * Decimal('3.45')  # Tarifa ejemplo
        
        bill, created = ElectricityBill.objects.get_or_create(
            tenant=tenant,
            bill_month=bill_date,
            defaults={
                'kwh_consumed': Decimal(str(kwh_base)),
                'amount': amount_base,
                'previous_reading': Decimal(str(kwh_base * i)),
                'current_reading': Decimal(str(kwh_base * (i + 1))),
                'due_date': bill_date + timedelta(days=20),
                'status': 'pagado' if i > 0 else 'pendiente',
                'paid_date': bill_date + timedelta(days=15) if i > 0 else None,
            }
        )
        if created:
            print(f"✓ Recibo de luz creado: {bill_date.strftime('%m/%Y')} - ${bill.amount}")
    
    # Crear incidencias de ejemplo
    incidents_data = [
        {
            'subject': 'Aire acondicionado no enfría lo suficiente',
            'category': 'temperatura',
            'description': 'El aire acondicionado de la oficina no está enfriando adecuadamente. La temperatura se mantiene alrededor de 26°C a pesar de estar configurado en 20°C.',
            'urgency_level': 3,
            'location_details': 'Oficina principal, zona de escritorios',
            'status': 'en_proceso',
        },
        {
            'subject': 'Luz fluorescente parpadeando',
            'category': 'iluminacion',
            'description': 'Una de las lámparas fluorescentes del techo parpadea constantemente, lo que está causando molestias para trabajar.',
            'urgency_level': 2,
            'location_details': 'Área de recepción',
            'status': 'reportada',
        },
        {
            'subject': 'Fuga de agua en el baño',
            'category': 'mantenimiento',
            'description': 'Hay una pequeña fuga en la llave del lavamanos del baño. El agua gotea constantemente.',
            'urgency_level': 4,
            'location_details': 'Baño de la oficina 502',
            'status': 'asignada',
        },
        {
            'subject': 'Problema con la impresora de red',
            'category': 'otros',
            'description': 'La impresora compartida no está respondiendo correctamente. Los documentos se quedan en cola y no se imprimen.',
            'urgency_level': 2,
            'location_details': 'Sala de copiado',
            'status': 'completada',
            'resolution_notes': 'Se reinició el servidor de impresión y se actualizaron los drivers. El problema ha sido resuelto.',
        }
    ]
    
    for inc_data in incidents_data:
        incident, created = TenantIncident.objects.get_or_create(
            tenant=tenant,
            subject=inc_data['subject'],
            defaults={
                'category': inc_data['category'],
                'description': inc_data['description'],
                'urgency_level': inc_data['urgency_level'],
                'location_details': inc_data['location_details'],
                'status': inc_data['status'],
                'reported_by': user,
                'resolution_notes': inc_data.get('resolution_notes', ''),
                'resolved_at': timezone.now() - timedelta(hours=2) if inc_data['status'] == 'completada' else None,
            }
        )
        if created:
            print(f"✓ Incidencia creada: {incident.subject}")
    
    # Crear registros de acceso de ejemplo
    for i in range(20):
        access_date = timezone.now() - timedelta(hours=i*6, minutes=i*15)
        access_type = 'entrada' if i % 2 == 0 else 'salida'
        
        access, created = TenantAccess.objects.get_or_create(
            tenant=tenant,
            user=user,
            access_time=access_date,
            defaults={
                'access_type': access_type,
                'location': 'Entrada Principal',
            }
        )
        if created and i < 5:  # Solo mostrar los primeros 5
            print(f"✓ Acceso registrado: {access_type} - {access_date.strftime('%d/%m/%Y %H:%M')}")
    
    print(f"\n✅ ¡Datos de ejemplo creados exitosamente!")
    print(f"📋 Inquilino: {tenant.tenant_name}")
    print(f"👤 Usuario: {user.username} (contraseña: ejemplo123)")
    print(f"📧 Email: {user.email}")
    print(f"\n🔗 Para probar el sistema, inicia sesión con el usuario creado.")

if __name__ == '__main__':
    create_sample_data()
