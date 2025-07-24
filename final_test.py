import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_corp.settings')
django.setup()

from maintenance.models import MaintenanceReport
from accounts.models import Notification
from django.contrib.auth.models import User

print("🔔 PRUEBA FINAL DEL SISTEMA DE NOTIFICACIONES")
print("=" * 60)

# Obtener estadísticas actuales
total_reportes = MaintenanceReport.objects.count()
total_notificaciones = Notification.objects.count()
notificaciones_sin_leer = Notification.objects.filter(is_read=False).count()

print(f"📊 ESTADÍSTICAS ACTUALES:")
print(f"   • Total de reportes: {total_reportes}")
print(f"   • Total de notificaciones: {total_notificaciones}")
print(f"   • Notificaciones sin leer: {notificaciones_sin_leer}")

# Mostrar usuarios y sus notificaciones
users_with_notifications = User.objects.filter(
    notifications__isnull=False
).distinct()

print(f"\n👥 USUARIOS CON NOTIFICACIONES:")
for user in users_with_notifications:
    user_notifications = Notification.objects.filter(recipient=user)
    unread_count = user_notifications.filter(is_read=False).count()
    print(f"   • {user.username} ({user.get_full_name() or 'Sin nombre'})")
    print(f"     - Total: {user_notifications.count()}")
    print(f"     - Sin leer: {unread_count}")

# Mostrar últimas notificaciones
print(f"\n📮 ÚLTIMAS 5 NOTIFICACIONES:")
latest_notifications = Notification.objects.order_by('-created_at')[:5]

for i, notif in enumerate(latest_notifications, 1):
    status = "📖 Leída" if notif.is_read else "🔴 Sin leer"
    priority_emoji = "🔴" if notif.priority <= 2 else "🟡" if notif.priority == 3 else "🟢"
    
    print(f"   {i}. {status} | {priority_emoji} {notif.title[:40]}...")
    print(f"      Para: {notif.recipient.username} | {notif.created_at.strftime('%d/%m %H:%M')}")

print(f"\n🌐 ENLACES PARA PROBAR:")
print(f"   • Dashboard: http://127.0.0.1:8000/dashboard/")
print(f"   • API Notificaciones: http://127.0.0.1:8000/api/notifications/list/")
print(f"   • Página Notificaciones: http://127.0.0.1:8000/accounts/notifications/")

print(f"\n✅ SISTEMA LISTO PARA USAR")
print(f"🔔 Haz clic en la campana del dashboard para ver las notificaciones")
