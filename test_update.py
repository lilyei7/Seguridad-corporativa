import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_corp.settings')
django.setup()

from maintenance.models import MaintenanceReport
from accounts.models import Notification

# Buscar el último reporte
report = MaintenanceReport.objects.last()
print(f'Actualizando reporte: {report.id} - {report.title}')
print(f'Estado actual: {report.status}')

# Cambiar estado
report.status = 'en_progreso'
report.save()

print(f'Nuevo estado: {report.status}')
print(f'Notificaciones totales para este reporte: {Notification.objects.filter(maintenance_report=report).count()}')

# Mostrar las últimas notificaciones
latest_notifs = Notification.objects.filter(maintenance_report=report).order_by('-created_at')[:3]
for notif in latest_notifs:
    print(f'- {notif.title} para {notif.recipient.username} ({notif.created_at})')
