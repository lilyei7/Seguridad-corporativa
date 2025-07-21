from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserRole
from tenants.models import Tenant


class Command(BaseCommand):
    help = 'Vincula usuarios inquilinos con sus perfiles de Tenant correspondientes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra lo que se haría sin hacer cambios reales',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Procesar solo un usuario específico por su username',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        specific_user = options.get('user')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Modo DRY RUN - No se harán cambios reales'))
        
        self.stdout.write('Vinculando usuarios inquilinos con sus perfiles...')
        
        # Obtener usuarios con rol de inquilino
        tenant_users = UserRole.objects.filter(role='tenant', is_active=True)
        
        if specific_user:
            tenant_users = tenant_users.filter(user__username=specific_user)
            if not tenant_users.exists():
                self.stdout.write(
                    self.style.ERROR(f'No se encontró usuario "{specific_user}" con rol de inquilino')
                )
                return
        
        for user_role in tenant_users:
            user = user_role.user
            self.stdout.write(f'\n--- Procesando usuario: {user.username} ---')
            
            # Verificar si ya tiene un tenant vinculado en el UserRole
            if user_role.tenant_profile:
                self.stdout.write(f'  ✓ Ya tiene tenant vinculado: {user_role.tenant_profile}')
                continue
            
            # Buscar tenant por diferentes criterios
            tenant = None
            
            # 1. Buscar por assigned_user
            tenant = Tenant.objects.filter(assigned_user=user).first()
            if tenant:
                self.stdout.write(f'  → Encontrado por assigned_user: {tenant}')
            
            # 2. Buscar por email
            if not tenant and user.email:
                tenant = Tenant.objects.filter(contact_email=user.email).first()
                if tenant:
                    self.stdout.write(f'  → Encontrado por email: {tenant}')
            
            # 3. Buscar por nombre similar
            if not tenant and (user.first_name or user.last_name):
                full_name = f"{user.first_name} {user.last_name}".strip()
                if full_name:
                    # Buscar en tenant_name o contact_person
                    potential_tenants = Tenant.objects.filter(
                        tenant_name__icontains=user.first_name
                    ) | Tenant.objects.filter(
                        contact_person__icontains=user.first_name
                    ) | Tenant.objects.filter(
                        tenant_name__icontains=user.last_name
                    ) | Tenant.objects.filter(
                        contact_person__icontains=user.last_name
                    )
                    
                    if potential_tenants.count() == 1:
                        tenant = potential_tenants.first()
                        self.stdout.write(f'  → Encontrado por nombre: {tenant}')
                    elif potential_tenants.count() > 1:
                        self.stdout.write(f'  ⚠ Múltiples coincidencias por nombre ({potential_tenants.count()}):')
                        for pt in potential_tenants:
                            self.stdout.write(f'    - {pt}')
            
            # 4. Para Ana García específicamente
            if not tenant and user.username in ['inquilino1', 'ana_garcia', 'anagarcia']:
                potential_ana = Tenant.objects.filter(
                    tenant_name__icontains='ana'
                ) | Tenant.objects.filter(
                    contact_person__icontains='ana'
                ) | Tenant.objects.filter(
                    tenant_name__icontains='garcia'
                ) | Tenant.objects.filter(
                    contact_person__icontains='garcia'
                ) | Tenant.objects.filter(
                    tenant_name__icontains='farmacia'
                ) | Tenant.objects.filter(
                    tenant_name__icontains='san josé'
                )
                
                if potential_ana.exists():
                    tenant = potential_ana.first()
                    self.stdout.write(f'  → Encontrado para Ana García: {tenant}')
            
            if tenant:
                # Vincular en el UserRole
                if not dry_run:
                    user_role.tenant_profile = tenant
                    user_role.save()
                    
                    # También asegurar que el tenant tenga assigned_user
                    if not tenant.assigned_user:
                        tenant.assigned_user = user
                        tenant.save()
                        self.stdout.write(f'  ✓ Usuario asignado al tenant')
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Vinculación completada: {user.username} ↔ {tenant}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  (DRY RUN) Se vincularía: {user.username} ↔ {tenant}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ No se encontró tenant para {user.username}')
                )
                
                # Mostrar información disponible para ayudar a identificar
                self.stdout.write(f'    - Email: {user.email or "No especificado"}')
                self.stdout.write(f'    - Nombre: {user.get_full_name() or "No especificado"}')
                
                # Sugerir crear tenant si es necesario
                if not dry_run:
                    self.stdout.write(f'    - Considera crear un tenant para este usuario')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Vinculación completada'))
        
        if not dry_run:
            self.show_summary()
        else:
            self.stdout.write(self.style.WARNING('Ejecuta sin --dry-run para aplicar los cambios'))
    
    def show_summary(self):
        self.stdout.write('\n--- RESUMEN FINAL ---')
        
        # Usuarios con rol de inquilino
        tenant_users = UserRole.objects.filter(role='tenant', is_active=True)
        total_tenant_users = tenant_users.count()
        linked_users = tenant_users.filter(tenant_profile__isnull=False).count()
        unlinked_users = total_tenant_users - linked_users
        
        self.stdout.write(f'Total usuarios inquilinos: {total_tenant_users}')
        self.stdout.write(f'Usuarios vinculados: {linked_users}')
        if unlinked_users > 0:
            self.stdout.write(self.style.WARNING(f'Usuarios sin vincular: {unlinked_users}'))
        
        # Tenants con usuario asignado
        total_tenants = Tenant.objects.count()
        assigned_tenants = Tenant.objects.filter(assigned_user__isnull=False).count()
        unassigned_tenants = total_tenants - assigned_tenants
        
        self.stdout.write(f'\nTotal tenants: {total_tenants}')
        self.stdout.write(f'Tenants con usuario asignado: {assigned_tenants}')
        if unassigned_tenants > 0:
            self.stdout.write(self.style.WARNING(f'Tenants sin usuario: {unassigned_tenants}'))
