import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_corp.settings')
django.setup()

from maintenance.models import MaintenanceReport, MaintenanceArea
from django.contrib.auth.models import User
from accounts.models import Notification

print("🧪 PROBANDO SISTEMA DE NOTIFICACIONES MEJORADO")
print("=" * 60)

# Crear un nuevo reporte para probar
area = MaintenanceArea.objects.first()
user = User.objects.get(username='1')

print(f"📝 Creando nuevo reporte...")
report = MaintenanceReport.objects.create(
    title='Prueba sistema notificaciones mejorado',
    description='Probando el nuevo sistema con UI mejorada',
    category='electricidad',
    area=area,
    reported_by=user,
    contact_email='test@example.com',
    priority=2  # ALTA
)

print(f"✅ Reporte creado: {report.id} - {report.title}")

# Verificar notificaciones creadas
notifs = Notification.objects.filter(maintenance_report=report)
print(f"📧 Notificaciones creadas: {notifs.count()}")

for notif in notifs:
    print(f"   - Para: {notif.recipient.username}")
    print(f"   - Título: {notif.title}")
    print(f"   - Mensaje: {notif.message}")
    print(f"   - Prioridad: {notif.priority}")
    print()

# Cambiar estado para probar notificación de actualización
print(f"🔄 Cambiando estado del reporte...")
report.status = 'completado'
report.response_to_tenant = 'El problema ha sido resuelto exitosamente.'
report.save()

# Verificar nueva notificación
new_notifs = Notification.objects.filter(maintenance_report=report).order_by('-created_at')
print(f"📧 Total de notificaciones ahora: {new_notifs.count()}")

latest = new_notifs.first()
if latest:
    print(f"📬 Última notificación:")
    print(f"   - Para: {latest.recipient.username}")
    print(f"   - Título: {latest.title}")
    print(f"   - Mensaje: {latest.message}")

# Estadísticas generales
total_unread = Notification.objects.filter(is_read=False).count()
print(f"\n📊 ESTADÍSTICAS:")
print(f"   - Total notificaciones sin leer: {total_unread}")
print(f"   - Total reportes en BD: {MaintenanceReport.objects.count()}")

print(f"\n🌐 Abre el navegador en: http://127.0.0.1:8000/dashboard/")
print(f"🔔 Las notificaciones deberían aparecer en la campana del header")
print("✨ ¡Sistema de notificaciones mejorado listo!")
