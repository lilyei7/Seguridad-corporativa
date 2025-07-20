from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tenants.models import Tenant
from guards.models import Guard
from visits.models import Visit
from datetime import date, time, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Crea datos de prueba para el sistema SecureCorp'

    def handle(self, *args, **options):
        # Crear usuarios para vigilantes si no existen
        guard_users = []
        for i, (first_name, last_name) in enumerate([
            ('Carlos', 'Mendoza'),
            ('Sofia', 'Ramírez'),
            ('Javier', 'López'),
            ('Ana', 'García'),
            ('Ricardo', 'Torres')
        ], 1):
            username = f'{first_name.lower()}.{last_name.lower()}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f'{username}@securecorp.com',
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Usuario creado: {username}')
            guard_users.append(user)

        # Crear vigilantes
        guard_positions = ['supervisor', 'vigilante', 'vigilante', 'vigilante', 'vigilante']
        guard_statuses = ['activo', 'activo', 'inactivo', 'activo', 'activo']
        
        for i, user in enumerate(guard_users):
            guard, created = Guard.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': f'EMP{1000 + i}',
                    'position': guard_positions[i],
                    'status': guard_statuses[i],
                    'phone': f'+52 555 {1000 + i}{1000 + i}',
                    'emergency_contact': f'Contacto de {user.first_name}',
                    'emergency_phone': f'+52 555 {2000 + i}{2000 + i}',
                    'hire_date': date.today() - timedelta(days=30 * (i + 1))
                }
            )
            if created:
                self.stdout.write(f'Vigilante creado: {user.get_full_name()}')

        # Crear inquilinos de prueba
        tenants_data = [
            {
                'tenant_name': 'Corporativo Azteca',
                'contact_person': 'María González',
                'contact_email': 'maria.gonzalez@azteca.com',
                'contact_phone': '+52 555 1234567',
                'address': 'Av. Reforma 123, Piso 15',
                'city': 'Ciudad de México',
                'state': 'CDMX',
                'zip_code': '06600'
            },
            {
                'tenant_name': 'Tecnología Avanzada S.A.',
                'contact_person': 'Roberto Silva',
                'contact_email': 'roberto.silva@tecavanzada.com',
                'contact_phone': '+52 555 2345678',
                'address': 'Blvd. Tecnológico 456, Torre B',
                'city': 'Guadalajara',
                'state': 'Jalisco',
                'zip_code': '44100'
            },
            {
                'tenant_name': 'Consultoría Estratégica',
                'contact_person': 'Laura Martínez',
                'contact_email': 'laura.martinez@consestrategica.com',
                'contact_phone': '+52 555 3456789',
                'address': 'Calle Principal 789, Oficina 300',
                'city': 'Monterrey',
                'state': 'Nuevo León',
                'zip_code': '64000'
            }
        ]

        for tenant_data in tenants_data:
            tenant, created = Tenant.objects.get_or_create(
                tenant_name=tenant_data['tenant_name'],
                defaults=tenant_data
            )
            if created:
                self.stdout.write(f'Inquilino creado: {tenant.tenant_name}')

        # Crear visitas de prueba
        tenants = Tenant.objects.all()
        guards = Guard.objects.filter(status='activo')
        
        visits_data = [
            {
                'visitor_name': 'Juan Pérez',
                'visitor_email': 'juan.perez@email.com',
                'visitor_phone': '+52 555 1111111',
                'visitor_company': 'Proveedores Unidos',
                'purpose': 'Reunión de negocios con el equipo directivo',
                'visit_type': 'reunion',
                'scheduled_date': date.today(),
                'scheduled_time': time(10, 0),
                'status': 'pendiente'
            },
            {
                'visitor_name': 'Ana López',
                'visitor_email': 'ana.lopez@email.com',
                'visitor_phone': '+52 555 2222222',
                'visitor_company': 'Servicios Técnicos',
                'purpose': 'Mantenimiento de equipos de cómputo',
                'visit_type': 'mantenimiento',
                'scheduled_date': date.today(),
                'scheduled_time': time(14, 30),
                'status': 'completada'
            },
            {
                'visitor_name': 'Alejandro Vargas',
                'visitor_email': 'alejandro.vargas@email.com',
                'visitor_phone': '+52 555 3333333',
                'visitor_company': 'Entregas Express',
                'purpose': 'Entrega de documentos importantes',
                'visit_type': 'entrega',
                'scheduled_date': date.today() - timedelta(days=1),
                'scheduled_time': time(9, 15),
                'status': 'cancelada'
            },
            {
                'visitor_name': 'Carmen Ruiz',
                'visitor_email': 'carmen.ruiz@email.com',
                'visitor_phone': '+52 555 4444444',
                'visitor_company': 'Consultores Independientes',
                'purpose': 'Presentación de proyecto de consultoría',
                'visit_type': 'trabajo',
                'scheduled_date': date.today() + timedelta(days=1),
                'scheduled_time': time(11, 0),
                'status': 'pendiente'
            }
        ]

        for i, visit_data in enumerate(visits_data):
            if tenants and guards:
                visit_data['tenant'] = tenants[i % len(tenants)]
                if visit_data['status'] in ['completada', 'en_progreso']:
                    visit_data['registered_by'] = guards[0]
                
                visit, created = Visit.objects.get_or_create(
                    visitor_name=visit_data['visitor_name'],
                    scheduled_date=visit_data['scheduled_date'],
                    defaults=visit_data
                )
                if created:
                    self.stdout.write(f'Visita creada: {visit.visitor_name}')

        self.stdout.write(
            self.style.SUCCESS('¡Datos de prueba creados exitosamente!')
        )
