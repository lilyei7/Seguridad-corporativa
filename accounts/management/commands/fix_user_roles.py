from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from accounts.models import UserRole
from tenants.models import Tenant
from guards.models import Guard


class Command(BaseCommand):
    help = 'Corrige y asigna roles de usuario basados en sus perfiles existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra lo que se haría sin hacer cambios reales',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Modo DRY RUN - No se harán cambios reales'))
        
        self.stdout.write('Iniciando corrección de roles de usuario...')
        
        # Obtener todos los usuarios
        users = User.objects.all()
        
        for user in users:
            self.stdout.write(f'\n--- Procesando usuario: {user.username} ---')
            
            # Verificar si ya tiene un UserRole
            existing_role = UserRole.objects.filter(user=user).first()
            if existing_role:
                self.stdout.write(f'  ✓ Ya tiene rol: {existing_role.get_role_display()}')
                continue
            
            # Determinar el rol basado en perfiles existentes
            role = None
            
            # Verificar si es superusuario
            if user.is_superuser:
                role = 'admin'
                self.stdout.write(f'  → Es superusuario, asignando rol: admin')
            
            # Verificar si tiene perfil de inquilino
            elif hasattr(user, 'tenant_profile') or Tenant.objects.filter(assigned_user=user).exists():
                role = 'tenant'
                self.stdout.write(f'  → Tiene perfil de inquilino, asignando rol: tenant')
            
            # Verificar si tiene perfil de vigilante
            elif hasattr(user, 'guard_profile') or Guard.objects.filter(user=user).exists():
                role = 'guard'
                self.stdout.write(f'  → Tiene perfil de vigilante, asignando rol: guard')
            
            # Verificar grupos
            elif user.groups.exists():
                group_names = [g.name.lower() for g in user.groups.all()]
                self.stdout.write(f'  → Grupos: {", ".join(group_names)}')
                
                if any('inquilino' in name or 'tenant' in name for name in group_names):
                    role = 'tenant'
                    self.stdout.write(f'  → Basado en grupos, asignando rol: tenant')
                elif any('vigilante' in name or 'guard' in name for name in group_names):
                    role = 'guard'
                    self.stdout.write(f'  → Basado en grupos, asignando rol: guard')
                elif any('admin' in name or 'administrador' in name for name in group_names):
                    role = 'admin'
                    self.stdout.write(f'  → Basado en grupos, asignando rol: admin')
                elif any('mantenimiento' in name or 'maintenance' in name for name in group_names):
                    role = 'maintenance'
                    self.stdout.write(f'  → Basado en grupos, asignando rol: maintenance')
                elif any('recepcion' in name or 'reception' in name for name in group_names):
                    role = 'reception'
                    self.stdout.write(f'  → Basado en grupos, asignando rol: reception')
            
            # Si no se pudo determinar, asignar rol por defecto
            if not role:
                role = 'tenant'  # Rol por defecto
                self.stdout.write(f'  → No se pudo determinar, asignando rol por defecto: tenant')
            
            # Crear el UserRole
            if not dry_run:
                user_role = UserRole.objects.create(
                    user=user,
                    role=role,
                    is_active=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Rol creado: {user_role.get_role_display()}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  (DRY RUN) Se crearía rol: {role}')
                )
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Corrección de roles completada'))
        
        # Mostrar resumen
        if not dry_run:
            self.show_summary()
        else:
            self.stdout.write(self.style.WARNING('Ejecuta sin --dry-run para aplicar los cambios'))
    
    def show_summary(self):
        self.stdout.write('\n--- RESUMEN FINAL ---')
        
        role_counts = {}
        for role_choice in UserRole.ROLE_CHOICES:
            role_key = role_choice[0]
            role_name = role_choice[1]
            count = UserRole.objects.filter(role=role_key, is_active=True).count()
            role_counts[role_name] = count
            self.stdout.write(f'{role_name}: {count} usuarios')
        
        # Mostrar usuarios sin rol
        users_without_role = User.objects.filter(user_role__isnull=True).count()
        if users_without_role > 0:
            self.stdout.write(self.style.WARNING(f'Sin rol asignado: {users_without_role} usuarios'))
        
        self.stdout.write(f'\nTotal de usuarios: {User.objects.count()}')
        self.stdout.write(f'Total con roles: {UserRole.objects.filter(is_active=True).count()}')
