from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserRole
from tenants.models import Tenant


class Command(BaseCommand):
    help = 'Verifica el estado general del sistema de roles y usuarios'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Verificando estado del sistema...\n')
        
        # Verificar usuarios específicos
        self.check_specific_users()
        
        # Verificar integridad del sistema
        self.check_system_integrity()
        
        # Verificar vinculaciones
        self.check_user_tenant_links()
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ Verificación completada'))
    
    def check_specific_users(self):
        self.stdout.write('👥 Verificando usuarios específicos:')
        
        # Lista de usuarios clave para verificar
        key_users = ['inquilino1', 'inquilino2', 'vigilante1', 'vigilante2', 'admin']
        
        for username in key_users:
            try:
                user = User.objects.get(username=username)
                user_role = getattr(user, 'user_role', None)
                
                self.stdout.write(f'\n  Usuario: {username}')
                self.stdout.write(f'    ID: {user.id}')
                self.stdout.write(f'    Email: {user.email or "No especificado"}')
                self.stdout.write(f'    Activo: {"✓" if user.is_active else "✗"}')
                
                if user_role:
                    self.stdout.write(f'    Rol: {user_role.get_role_display()} ({"✓ Activo" if user_role.is_active else "✗ Inactivo"})')
                    
                    if user_role.role == 'tenant' and user_role.tenant_profile:
                        tenant = user_role.tenant_profile
                        self.stdout.write(f'    Local: {tenant.tenant_name}')
                        self.stdout.write(f'    Oficina: {tenant.numero_oficina or "No especificada"}')
                    elif user_role.role == 'tenant':
                        self.stdout.write('    ⚠️  Inquilino sin local asignado')
                else:
                    self.stdout.write('    ❌ Sin rol asignado')
                
                # Verificar grupos
                groups = user.groups.all()
                if groups:
                    group_names = [g.name for g in groups]
                    self.stdout.write(f'    Grupos: {", ".join(group_names)}')
                else:
                    self.stdout.write('    Grupos: Ninguno')
                    
            except User.DoesNotExist:
                self.stdout.write(f'  ❌ Usuario {username} no encontrado')
    
    def check_system_integrity(self):
        self.stdout.write('\n🔧 Verificando integridad del sistema:')
        
        # Contadores
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        users_with_roles = UserRole.objects.filter(is_active=True).count()
        users_without_roles = total_users - UserRole.objects.count()
        
        self.stdout.write(f'\n  📊 Estadísticas generales:')
        self.stdout.write(f'    Total usuarios: {total_users}')
        self.stdout.write(f'    Usuarios activos: {active_users}')
        self.stdout.write(f'    Usuarios con roles: {users_with_roles}')
        if users_without_roles > 0:
            self.stdout.write(f'    ⚠️  Usuarios sin roles: {users_without_roles}')
        
        # Por tipo de rol
        role_stats = {}
        for role_choice in UserRole.ROLE_CHOICES:
            role_key = role_choice[0]
            role_name = role_choice[1]
            count = UserRole.objects.filter(role=role_key, is_active=True).count()
            role_stats[role_name] = count
        
        self.stdout.write(f'\n  📋 Distribución por roles:')
        for role_name, count in role_stats.items():
            self.stdout.write(f'    {role_name}: {count} usuarios')
        
        # Verificar roles problemáticos
        problematic_roles = UserRole.objects.filter(is_active=False)
        if problematic_roles:
            self.stdout.write(f'\n  ⚠️  Roles inactivos encontrados: {problematic_roles.count()}')
    
    def check_user_tenant_links(self):
        self.stdout.write('\n🏢 Verificando vinculaciones usuario-inquilino:')
        
        # Inquilinos en el sistema
        total_tenants = Tenant.objects.count()
        active_tenants = Tenant.objects.filter(is_active=True).count()
        tenants_with_users = Tenant.objects.filter(assigned_user__isnull=False).count()
        
        self.stdout.write(f'\n  📊 Estadísticas de inquilinos:')
        self.stdout.write(f'    Total inquilinos: {total_tenants}')
        self.stdout.write(f'    Inquilinos activos: {active_tenants}')
        self.stdout.write(f'    Inquilinos con usuario: {tenants_with_users}')
        
        # Usuarios inquilinos
        tenant_users = UserRole.objects.filter(role='tenant', is_active=True)
        linked_tenant_users = tenant_users.filter(tenant_profile__isnull=False).count()
        unlinked_tenant_users = tenant_users.count() - linked_tenant_users
        
        self.stdout.write(f'\n  👥 Usuarios inquilinos:')
        self.stdout.write(f'    Total usuarios inquilinos: {tenant_users.count()}')
        self.stdout.write(f'    Usuarios vinculados: {linked_tenant_users}')
        if unlinked_tenant_users > 0:
            self.stdout.write(f'    ⚠️  Usuarios sin vincular: {unlinked_tenant_users}')
        
        # Mostrar vinculaciones específicas
        self.stdout.write(f'\n  🔗 Vinculaciones activas:')
        for user_role in tenant_users.filter(tenant_profile__isnull=False):
            user = user_role.user
            tenant = user_role.tenant_profile
            self.stdout.write(f'    {user.username} ↔ {tenant.tenant_name}')
        
        # Detectar problemas potenciales
        self.detect_potential_issues()
    
    def detect_potential_issues(self):
        self.stdout.write('\n🚨 Detectando problemas potenciales:')
        
        issues_found = False
        
        # Usuarios sin email
        users_no_email = User.objects.filter(email='').count()
        if users_no_email > 0:
            self.stdout.write(f'    ⚠️  {users_no_email} usuarios sin email configurado')
            issues_found = True
        
        # Inquilinos sin usuario asignado
        unassigned_tenants = Tenant.objects.filter(assigned_user__isnull=True, is_active=True)
        if unassigned_tenants:
            self.stdout.write(f'    ⚠️  {unassigned_tenants.count()} inquilinos sin usuario asignado:')
            for tenant in unassigned_tenants[:5]:  # Mostrar solo los primeros 5
                self.stdout.write(f'      - {tenant.tenant_name}')
            issues_found = True
        
        # Usuarios inquilinos sin tenant vinculado
        unlinked_users = UserRole.objects.filter(
            role='tenant', 
            is_active=True, 
            tenant_profile__isnull=True
        )
        if unlinked_users:
            self.stdout.write(f'    ⚠️  {unlinked_users.count()} usuarios inquilinos sin local vinculado:')
            for user_role in unlinked_users:
                self.stdout.write(f'      - {user_role.user.username}')
            issues_found = True
        
        # Usuarios superusuarios sin rol
        superusers_no_role = User.objects.filter(
            is_superuser=True,
            user_role__isnull=True
        )
        if superusers_no_role:
            self.stdout.write(f'    ℹ️  {superusers_no_role.count()} superusuarios sin rol específico:')
            for user in superusers_no_role:
                self.stdout.write(f'      - {user.username}')
        
        if not issues_found:
            self.stdout.write('    ✅ No se encontraron problemas evidentes')
        else:
            self.stdout.write('\n    💡 Sugerencias:')
            self.stdout.write('      - Ejecuta "python manage.py fix_user_roles" para corregir roles')
            self.stdout.write('      - Ejecuta "python manage.py link_tenant_users" para vincular inquilinos')
            self.stdout.write('      - Revisa manualmente las configuraciones específicas')
