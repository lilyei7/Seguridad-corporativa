from django.contrib.auth.models import User
from accounts.models import UserRole, Notification, UserPreferences

# Crear usuarios de ejemplo
users_data = [
    {'username': 'admin_user', 'email': 'admin@olchatec.com', 'first_name': 'Administrador', 'last_name': 'Principal', 'role': 'admin'},
    {'username': 'tenant_user', 'email': 'inquilino@ejemplo.com', 'first_name': 'Juan', 'last_name': 'Perez', 'role': 'tenant'},
    {'username': 'guard_user', 'email': 'vigilante@ejemplo.com', 'first_name': 'Carlos', 'last_name': 'Rodriguez', 'role': 'guard'},
]

created_users = []

for user_data in users_data:
    user, created = User.objects.get_or_create(
        username=user_data['username'],
        defaults={
            'email': user_data['email'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'is_active': True
        }
    )
    
    if created:
        user.set_password('admin123')
        user.save()
        print(f"Usuario creado: {user.username}")
    
    # Crear rol
    user_role, role_created = UserRole.objects.get_or_create(
        user=user,
        defaults={'role': user_data['role'], 'is_active': True}
    )
    
    if role_created:
        print(f"Rol asignado: {user.username} -> {user_data['role']}")
    
    created_users.append(user)

# Crear notificaciones para admin
admin_user = User.objects.filter(role_profile__role='admin', role_profile__is_active=True).first()

if admin_user:
    notifications_data = [
        {'title': 'Bienvenido al Sistema', 'message': 'Sistema configurado correctamente.', 'notification_type': 'system_alert', 'priority': 'medium'},
        {'title': 'Solicitud de Mantenimiento', 'message': 'Nueva solicitud de aire acondicionado.', 'notification_type': 'maintenance_request', 'priority': 'high'},
        {'title': 'Reporte de Incidente', 'message': 'Incidente en estacionamiento.', 'notification_type': 'incident_report', 'priority': 'urgent'},
    ]
    
    for notif_data in notifications_data:
        notification, created = Notification.objects.get_or_create(
            recipient=admin_user,
            title=notif_data['title'],
            defaults={
                'message': notif_data['message'],
                'notification_type': notif_data['notification_type'],
                'priority': notif_data['priority'],
                'is_read': False
            }
        )
        
        if created:
            print(f"Notificacion creada: {notif_data['title']}")

print("Inicializacion completada!")
print("Usuarios: admin_user, tenant_user, guard_user")
print("Contrasena: admin123")
