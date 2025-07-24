import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_corp.settings')
django.setup()

from maintenance.models import MaintenanceReport
from django.contrib.auth.models import User

# Obtener usuarios
admin_user = User.objects.get(username='gema')  # Admin
tenant_user = User.objects.get(username='1')   # Tenant

print(f'Admin {admin_user.username}:')
print(f'- Is superuser: {admin_user.is_superuser}')
print(f'- Is staff: {admin_user.is_staff}')
print(f'- Groups: {[g.name for g in admin_user.groups.all()]}')

print(f'\nTenant {tenant_user.username}:')
print(f'- Is superuser: {tenant_user.is_superuser}')
print(f'- Is staff: {tenant_user.is_staff}')
print(f'- Groups: {[g.name for g in tenant_user.groups.all()]}')

print(f'\nTodos los reportes en BD: {MaintenanceReport.objects.count()}')
for report in MaintenanceReport.objects.all():
    print(f'- ID {report.id}: {report.title} (por {report.reported_by.username})')

# Simular la lógica de la vista
def check_admin_access(user):
    is_tenant = user.groups.filter(name='Tenant').exists()
    is_admin = user.is_superuser or user.is_staff or user.groups.filter(name='Admin').exists()
    
    if is_admin:
        return True, "Admin puede ver todos los reportes"
    elif is_tenant and not is_admin:
        return False, "Tenant solo ve sus reportes"
    else:
        return False, "Sin permisos"

admin_access, admin_msg = check_admin_access(admin_user)
tenant_access, tenant_msg = check_admin_access(tenant_user)

print(f'\nAcceso admin {admin_user.username}: {admin_access} - {admin_msg}')
print(f'Acceso tenant {tenant_user.username}: {tenant_access} - {tenant_msg}')
