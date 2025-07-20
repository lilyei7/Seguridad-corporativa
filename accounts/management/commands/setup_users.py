from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from guards.models import Guard
from tenants.models import Tenant

class Command(BaseCommand):
    help = 'Actualiza usuarios de ejemplo con grupos y asociaciones correctas'

    def handle(self, *args, **options):
        # Obtener grupos
        try:
            vigilantes_group = Group.objects.get(name='Vigilantes')
            inquilinos_group = Group.objects.get(name='Inquilinos')
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Los grupos no existen. Ejecuta setup_groups primero.')
            )
            return

        # Crear usuarios vigilantes
        vigilante_users = [
            {'username': 'vigilante1', 'email': 'vigilante1@olcha.com', 'first_name': 'Carlos', 'last_name': 'Mendoza'},
            {'username': 'vigilante2', 'email': 'vigilante2@olcha.com', 'first_name': 'Sofia', 'last_name': 'Ramírez'},
        ]

        for user_data in vigilante_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            if created:
                user.set_password('vigilante123')
                user.save()
                self.stdout.write(f"Usuario vigilante '{user.username}' creado")
            
            # Agregar al grupo
            user.groups.clear()
            user.groups.add(vigilantes_group)
            
            # Crear registro de guardia si no existe
            guard, guard_created = Guard.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': f'VIG{user.id:03d}',
                    'status': 'activo',
                    'position': 'vigilante',
                    'phone': f'+52 55 1234 567{user.id}',
                    'emergency_contact': 'Contacto de Emergencia',
                    'emergency_phone': '+52 55 9999 0000',
                    'hire_date': '2025-01-01',
                }
            )
            if guard_created:
                self.stdout.write(f"Registro de guardia para '{user.username}' creado")

        # Crear usuarios inquilinos
        inquilino_users = [
            {
                'username': 'inquilino1', 
                'email': 'local101@olcha.com', 
                'first_name': 'Ana', 
                'last_name': 'García',
                'tenant_name': 'Farmacia San José'
            },
            {
                'username': 'inquilino2', 
                'email': 'local205@olcha.com', 
                'first_name': 'Ricardo', 
                'last_name': 'Torres',
                'tenant_name': 'Consultorio Dental'
            },
        ]

        for user_data in inquilino_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            if created:
                user.set_password('inquilino123')
                user.save()
                self.stdout.write(f"Usuario inquilino '{user.username}' creado")
            
            # Agregar al grupo
            user.groups.clear()
            user.groups.add(inquilinos_group)
            
            # Actualizar o crear inquilino con email correcto
            try:
                tenant = Tenant.objects.get(contact_email=user.email)
                tenant.contact_person = f"{user.first_name} {user.last_name}"
                tenant.save()
                self.stdout.write(f"Inquilino '{tenant.tenant_name}' actualizado con usuario '{user.username}'")
            except Tenant.DoesNotExist:
                tenant = Tenant.objects.create(
                    tenant_name=user_data['tenant_name'],
                    contact_person=f"{user.first_name} {user.last_name}",
                    contact_email=user.email,
                    contact_phone=f'+52 55 9876 543{user.id}',
                    address=f'Local {user.id}01 - Centro Comercial',
                    city='Ciudad de México',
                    state='CDMX',
                    zip_code='01000',
                    is_active=True
                )
                self.stdout.write(f"Inquilino '{tenant.tenant_name}' creado para usuario '{user.username}'")

        # Actualizar credenciales
        self.stdout.write("\n" + "="*50)
        self.stdout.write("CREDENCIALES ACTUALIZADAS:")
        self.stdout.write("="*50)
        self.stdout.write("ADMINISTRADOR:")
        self.stdout.write("  Usuario: admin")
        self.stdout.write("  Contraseña: admin123")
        self.stdout.write("")
        self.stdout.write("VIGILANTES:")
        self.stdout.write("  Usuario: vigilante1 | Contraseña: vigilante123")
        self.stdout.write("  Usuario: vigilante2 | Contraseña: vigilante123")
        self.stdout.write("")
        self.stdout.write("INQUILINOS:")
        self.stdout.write("  Usuario: inquilino1 | Contraseña: inquilino123")
        self.stdout.write("  Usuario: inquilino2 | Contraseña: inquilino123")
        self.stdout.write("="*50)

        self.stdout.write(
            self.style.SUCCESS('\nUsuarios actualizados exitosamente!')
        )
