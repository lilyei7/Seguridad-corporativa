from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class Command(BaseCommand):
    help = 'Prueba todas las URLs del sistema'

    def handle(self, *args, **options):
        self.client = Client()
        
        self.stdout.write('🌐 Probando URLs del Sistema de Seguridad Corporativa\n')
        
        # URLs públicas (sin login)
        public_urls = [
            ('🔐 Login', '/login/'),
            ('🏠 Home', '/'),
        ]
        
        self.stdout.write('📂 URLs PÚBLICAS:')
        for name, url in public_urls:
            self.test_url(name, url, require_login=False)
        
        # Crear usuario de prueba si no existe
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.stdout.write('⚠️  Usuario admin no encontrado. Crear con: python manage.py createsuperuser')
            return
        
        # Login
        self.client.force_login(user)
        self.stdout.write('\n✅ Logueado como admin\n')
        
        # URLs principales por rol
        admin_urls = [
            ('👨‍💼 Panel Admin PC', '/administracion/'),
            ('📱 Panel Admin Móvil', '/admin-movil/'),
        ]
        
        tenant_urls = [
            ('🏠 Panel Inquilino PC', '/inquilino/'),
            ('📱 Panel Inquilino Móvil', '/inquilino-movil/'),
        ]
        
        guard_urls = [
            ('👮‍♂️ Panel Vigilante PC', '/vigilante/'),
            ('📱 Panel Vigilante Móvil', '/vigilante-movil/'),
        ]
        
        # APIs de notificaciones
        api_urls = [
            ('🔔 API Notificaciones', '/api/notifications/unread/'),
            ('📊 API Suscripciones', '/api/notifications/subscribe/'),
        ]
        
        self.stdout.write('📂 URLs ADMINISTRADOR:')
        for name, url in admin_urls:
            self.test_url(name, url)
        
        self.stdout.write('\n📂 URLs INQUILINO:')
        for name, url in tenant_urls:
            self.test_url(name, url)
        
        self.stdout.write('\n📂 URLs VIGILANTE:')
        for name, url in guard_urls:
            self.test_url(name, url)
        
        self.stdout.write('\n📂 APIs:')
        for name, url in api_urls:
            self.test_url(name, url, is_api=True)
        
        # Resumen
        self.stdout.write('\n📊 RESUMEN:')
        self.stdout.write(f'✅ URLs funcionando: {self.working_urls}')
        self.stdout.write(f'❌ URLs con problemas: {self.broken_urls}')
        self.stdout.write(f'📊 Total probadas: {self.total_urls}')
        
        if self.broken_urls == 0:
            self.stdout.write(self.style.SUCCESS('\n🎉 ¡Todas las URLs funcionan correctamente!'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠️  {self.broken_urls} URLs necesitan revisión'))

    def test_url(self, name, url, require_login=True, is_api=False):
        if not hasattr(self, 'working_urls'):
            self.working_urls = 0
            self.broken_urls = 0
            self.total_urls = 0
        
        self.total_urls += 1
        
        try:
            response = self.client.get(url)
            status = response.status_code
            
            # Determinar si es exitoso
            if is_api:
                success = status in [200, 201]
                error_codes = [404, 500]
            else:
                success = status in [200, 302]  # 302 = redirect
                error_codes = [404, 500]
            
            if success:
                status_icon = '✅'
                self.working_urls += 1
                status_text = f'OK ({status})'
            elif status in error_codes:
                status_icon = '❌'
                self.broken_urls += 1
                status_text = f'ERROR ({status})'
            else:
                status_icon = '⚠️'
                status_text = f'ADVERTENCIA ({status})'
            
            self.stdout.write(f'   {status_icon} {name}: {url} → {status_text}')
            
        except Exception as e:
            self.stdout.write(f'   ❌ {name}: {url} → EXCEPCIÓN: {str(e)}')
            self.broken_urls += 1
