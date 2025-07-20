from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from tenants.models import Tenant
from guards.models import Guard
from visits.models import Visit

class Command(BaseCommand):
    help = 'Crea los grupos de usuarios y asigna permisos básicos'

    def handle(self, *args, **options):
        # Crear grupos
        vigilantes_group, created = Group.objects.get_or_create(name='Vigilantes')
        inquilinos_group, created = Group.objects.get_or_create(name='Inquilinos')
        
        self.stdout.write(f"Grupo 'Vigilantes' {'creado' if created else 'ya existe'}")
        self.stdout.write(f"Grupo 'Inquilinos' {'creado' if created else 'ya existe'}")
        
        # Permisos para Vigilantes
        visit_content_type = ContentType.objects.get_for_model(Visit)
        guard_content_type = ContentType.objects.get_for_model(Guard)
        
        vigilante_permissions = [
            'view_visit',
            'change_visit',
            'add_visit',
            'view_guard',
        ]
        
        for perm_codename in vigilante_permissions:
            try:
                if perm_codename.endswith('_visit'):
                    permission = Permission.objects.get(
                        codename=perm_codename,
                        content_type=visit_content_type
                    )
                else:
                    permission = Permission.objects.get(
                        codename=perm_codename,
                        content_type=guard_content_type
                    )
                vigilantes_group.permissions.add(permission)
                self.stdout.write(f"Permiso '{perm_codename}' agregado a Vigilantes")
            except Permission.DoesNotExist:
                self.stdout.write(f"Permiso '{perm_codename}' no encontrado")
        
        # Permisos para Inquilinos
        tenant_content_type = ContentType.objects.get_for_model(Tenant)
        
        inquilino_permissions = [
            'view_visit',
            'add_visit',
            'view_tenant',
        ]
        
        for perm_codename in inquilino_permissions:
            try:
                if perm_codename.endswith('_visit'):
                    permission = Permission.objects.get(
                        codename=perm_codename,
                        content_type=visit_content_type
                    )
                else:
                    permission = Permission.objects.get(
                        codename=perm_codename,
                        content_type=tenant_content_type
                    )
                inquilinos_group.permissions.add(permission)
                self.stdout.write(f"Permiso '{perm_codename}' agregado a Inquilinos")
            except Permission.DoesNotExist:
                self.stdout.write(f"Permiso '{perm_codename}' no encontrado")
        
        self.stdout.write(
            self.style.SUCCESS('Grupos y permisos configurados exitosamente!')
        )
