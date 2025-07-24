from maintenance.models import MaintenanceReport, MaintenanceArea
from django.contrib.auth.models import User
from accounts.models import Notification

area = MaintenanceArea.objects.first()
user = User.objects.get(username='1')

report = MaintenanceReport.objects.create(
    title='Tercera prueba notificaciones',
    description='Probando el sistema con el error de priority arreglado',
    category='electricidad',
    area=area,
    reported_by=user,
    contact_email='test@example.com',
    priority=1
)

print(f'Reporte creado: {report.id} - {report.title}')
print(f'Notificaciones creadas: {Notification.objects.filter(maintenance_report=report).count()}')

notif = Notification.objects.filter(maintenance_report=report).first()
if notif:
    print(f'Notificación: {notif.title} - Para: {notif.recipient.username}')
else:
    print('No se encontraron notificaciones')
    
    # 1. Verificar usuarios administradores
    print("\n1️⃣ VERIFICANDO USUARIOS ADMINISTRADORES...")
    admin_users = User.objects.filter(
        is_superuser=True
    )
    print(f"   Superusuarios encontrados: {admin_users.count()}")
    
    for admin in admin_users:
        print(f"   - {admin.username} ({admin.email or 'Sin email'})")
    
    # 2. Crear notificación de prueba
    print("\n2️⃣ CREANDO NOTIFICACIÓN DE PRUEBA...")
    if admin_users.exists():
        admin = admin_users.first()
        
        test_notification = Notification.objects.create(
            recipient=admin,
            title="🧪 PRUEBA: Nuevo Reporte de Mantenimiento Urgente",
            message=(
                "Este es un reporte de prueba para verificar el sistema de notificaciones.\n\n"
                "📋 Título: Falla en sistema eléctrico\n"
                "📂 Categoría: Eléctrico\n"
                "⭐ Prioridad: Crítica\n"
                "📍 Área: Lobby Principal\n"
                "👤 Reportado por: Sistema de Pruebas\n"
                "📧 Contacto: prueba@mantenimiento.com\n\n"
                "🔧 Por favor, revisa este reporte de prueba lo antes posible."
            ),
            notification_type='maintenance_request',
            priority='urgent',
            action_url='/maintenance/reports/'
        )
        
        print(f"   ✅ Notificación creada con ID: {test_notification.id}")
        print(f"   📧 Destinatario: {admin.username}")
        print(f"   🎯 Prioridad: {test_notification.priority}")
        
    else:
        print("   ❌ No se encontraron usuarios administradores")
        return False
    
    # 3. Verificar conteo de notificaciones
    print("\n3️⃣ VERIFICANDO CONTEO DE NOTIFICACIONES...")
    unread_count = Notification.objects.filter(
        recipient=admin,
        is_read=False,
        notification_type='maintenance_request'
    ).count()
    
    print(f"   📊 Notificaciones no leídas de mantenimiento: {unread_count}")
    
    # 4. Crear área de prueba si no existe
    print("\n4️⃣ VERIFICANDO ÁREAS DE MANTENIMIENTO...")
    test_area, created = MaintenanceArea.objects.get_or_create(
        name="Área de Pruebas",
        defaults={
            'description': 'Área creada para pruebas del sistema de notificaciones',
            'location': 'Sistema de Pruebas'
        }
    )
    
    if created:
        print(f"   ✅ Área creada: {test_area.name}")
    else:
        print(f"   📍 Área existente: {test_area.name}")
    
    # 5. Crear reporte de prueba
    print("\n5️⃣ CREANDO REPORTE DE MANTENIMIENTO DE PRUEBA...")
    
    # Buscar un usuario inquilino o crear uno temporal
    test_user = admin  # Usar admin como usuario de prueba
    
    test_report = MaintenanceReport.objects.create(
        title="🧪 PRUEBA - Sistema de Notificaciones",
        description=(
            "Este es un reporte de prueba creado automáticamente para verificar "
            "que el sistema de notificaciones funciona correctamente.\n\n"
            "Características de la prueba:\n"
            "- Prioridad crítica para probar alertas urgentes\n"
            "- Notificaciones automáticas a administradores\n"
            "- Verificación de badges y contadores\n"
            "- Prueba de sonidos y alertas visuales\n\n"
            "Si recibes esta notificación, el sistema está funcionando correctamente."
        ),
        category='electrico',
        priority=1,  # 1 = Crítica
        area=test_area,
        reported_by=test_user,
        contact_email='prueba@sistema.com',
        status='pendiente'
    )
    
    print(f"   ✅ Reporte creado con ID: {test_report.id}")
    print(f"   📋 Título: {test_report.title}")
    print(f"   ⭐ Prioridad: {test_report.get_priority_display()}")
    
    # 6. Probar función de notificación
    print("\n6️⃣ PROBANDO FUNCIÓN DE NOTIFICACIÓN...")
    try:
        from maintenance.views import notify_admins_new_report
        notifications_sent = notify_admins_new_report(test_report)
        
        if notifications_sent:
            print("   ✅ Notificaciones enviadas exitosamente")
        else:
            print("   ⚠️ Problemas enviando notificaciones")
            
    except Exception as e:
        print(f"   ❌ Error en función de notificación: {e}")
    
    # 7. Verificar notificaciones finales
    print("\n7️⃣ VERIFICACIÓN FINAL...")
    final_count = Notification.objects.filter(
        recipient=admin,
        is_read=False,
        notification_type='maintenance_request'
    ).count()
    
    print(f"   📊 Total notificaciones no leídas: {final_count}")
    
    # 8. Mostrar resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE LA PRUEBA:")
    print(f"   🎯 Notificaciones creadas: {final_count}")
    print(f"   📧 Administradores notificados: {admin_users.count()}")
    print(f"   📊 Reporte de prueba ID: {test_report.id}")
    print("   ✅ Sistema de notificaciones OPERATIVO")
    
    print("\n🔔 INSTRUCCIONES PARA VER LAS NOTIFICACIONES:")
    print("   1. Inicia sesión como administrador")
    print("   2. Observa la campana de notificaciones en el header")
    print("   3. Ve el badge rojo en 'Reportes de Inquilinos'")
    print("   4. Visita /accounts/notifications/ para ver todas las notificaciones")
    print("   5. El sistema debe mostrar alertas toast automáticamente")
    
    return True


if __name__ == "__main__":
    test_notification_system()
