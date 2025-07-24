import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_corp.settings')
django.setup()

from maintenance.models import MaintenanceReport, MaintenanceArea
from django.contrib.auth.models import User
from accounts.models import Notification

area = MaintenanceArea.objects.first()
user = User.objects.get(username='1')

report = MaintenanceReport.objects.create(
    title='Prueba notificaciones nueva',
    description='Test del sistema de notificaciones',
    category='electricidad',
    area=area,
    reported_by=user,
    contact_email='test@example.com',
    priority=1
)

print(f'Reporte creado: {report.id} - {report.title}')
print(f'Notificaciones: {Notification.objects.filter(maintenance_report=report).count()}')

notif = Notification.objects.filter(maintenance_report=report).first()
if notif:
    print(f'Notificación: {notif.title} - Para: {notif.recipient.username}')
else:
    print('No se encontraron notificaciones')
