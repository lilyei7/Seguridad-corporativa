"""
Script para inicializar datos de prueba para el sistema de notificaciones y roles
"""

from django.contrib.auth.models import User
from accounts.models import UserRole, Notification, UserPreferences

def create_sample_data():
    """Crear datos de ejemplo para probar el sistema"""
    
    # Crear usuarios de ejemplo si no existen
    users_data = [
        {
            'username': 'admin_user',
            'email': 'admin@olchatec.com',
            'first_name': 'Administrador',
            'last_name': 'Principal',
            'role': 'admin'
        },
        {
            'username': 'tenant_user',
            'email': 'inquilino@ejemplo.com',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'role': 'tenant'
        },
        {
            'username': 'guard_user',
            'email': 'vigilante@ejemplo.com',
            'first_name': 'Carlos',
            'last_name': 'Rodríguez',
            'role': 'guard'
        },
        {
            'username': 'maintenance_user',
            'email': 'mantenimiento@ejemplo.com',
            'first_name': 'Luis',
            'last_name': 'González',
            'role': 'maintenance'
        }
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
            user.set_password('admin123')  # Contraseña por defecto
            user.save()
            print(f"✓ Usuario creado: {user.username}")
        else:
            print(f"- Usuario ya existe: {user.username}")
        
        # Crear rol de usuario
        user_role, role_created = UserRole.objects.get_or_create(
            user=user,
            defaults={
                'role': user_data['role'],
                'is_active': True
            }
        )
        
        if role_created:
            print(f"✓ Rol asignado: {user.username} -> {user_data['role']}")
        
        # Crear preferencias por defecto
        preferences, pref_created = UserPreferences.objects.get_or_create(
            user=user,
            defaults={
                'email_notifications': True,
                'push_notifications': True,
                'dashboard_layout': 'standard'
            }
        )
        
        if pref_created:
            print(f"✓ Preferencias creadas para: {user.username}")
        
        created_users.append(user)
    
    return created_users

def create_sample_notifications(users):
    """Crear notificaciones de ejemplo"""
    
    # Encontrar usuarios por rol
    admin_users = [u for u in users if hasattr(u, 'user_role') and u.user_role.role == 'admin']
    
    if not admin_users:
        print("No se encontraron usuarios admin, creando notificaciones generales...")
        admin_users = users[:1]  # Usar el primer usuario
    
    notifications_data = [
        {
            'title': 'Bienvenido al Sistema',
            'message': 'Bienvenido al sistema de seguridad corporativa Olcha Tecnología. Su cuenta ha sido configurada correctamente.',
            'notification_type': 'system_alert',
            'priority': 'medium'
        },
        {
            'title': 'Solicitud de Mantenimiento',
            'message': 'Nueva solicitud de mantenimiento de aire acondicionado en oficina 302.',
            'notification_type': 'maintenance_request',
            'priority': 'high'
        },
        {
            'title': 'Reporte de Incidente',
            'message': 'Reporte de incidente de seguridad en el estacionamiento. Requiere atención inmediata.',
            'notification_type': 'incident_report',
            'priority': 'urgent'
        },
        {
            'title': 'Visita Programada',
            'message': 'Visita programada para mañana a las 10:00 AM. Cliente: ABC Corp.',
            'notification_type': 'visit_notification',
            'priority': 'low'
        },
        {
            'title': 'Actualización del Sistema',
            'message': 'El sistema será actualizado esta noche a las 2:00 AM. Duración estimada: 30 minutos.',
            'notification_type': 'system_alert',
            'priority': 'medium'
        }
    ]
    
    for admin_user in admin_users:
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
                print(f"✓ Notificación creada: {notif_data['title']} para {admin_user.username}")

def main():
    """Función principal para ejecutar la inicialización"""
    print("🚀 Inicializando datos de ejemplo...")
    print("=" * 50)
    
    # Crear usuarios y roles
    users = create_sample_data()
    print("\n📧 Creando notificaciones de ejemplo...")
    print("-" * 30)
    
    # Crear notificaciones
    create_sample_notifications(users)
    
    print("\n✅ Inicialización completada!")
    print("\nUsuarios creados:")
    print("- admin_user (Administrador) - Contraseña: admin123")
    print("- tenant_user (Inquilino) - Contraseña: admin123") 
    print("- guard_user (Vigilante) - Contraseña: admin123")
    print("- maintenance_user (Mantenimiento) - Contraseña: admin123")
    print("\n🔐 Inicia sesión con cualquiera de estos usuarios para probar el sistema.")

if __name__ == '__main__':
    main()
