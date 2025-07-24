import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_corp.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

print("🔍 DIAGNÓSTICO DEL SISTEMA DE NOTIFICACIONES")
print("=" * 60)

# Test del cliente
client = Client()

# Hacer login como admin
user = User.objects.get(username='gema')
client.force_login(user)

print(f"👤 Usuario logueado: {user.username}")

# Probar la API
print(f"\n🌐 Probando API de notificaciones...")

try:
    response = client.get('/api/notifications/list/')
    print(f"📡 GET /api/notifications/list/")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success', False)}")
        print(f"   Notificaciones: {len(data.get('notifications', []))}")
        print(f"   Sin leer: {data.get('unread_count', 0)}")
        
        # Mostrar algunas notificaciones
        notifications = data.get('notifications', [])[:3]
        for i, notif in enumerate(notifications, 1):
            print(f"   {i}. {notif['title'][:50]}...")
            print(f"      Leída: {notif['is_read']}")
            print(f"      Prioridad: {notif['priority']}")
    else:
        print(f"   Error: {response.content.decode()}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Verificar URLs registradas
from django.conf import settings
from django.urls import get_resolver

print(f"\n🔗 URLs registradas en /api/:")
try:
    resolver = get_resolver()
    api_patterns = []
    
    for pattern in resolver.url_patterns:
        if hasattr(pattern, 'pattern') and str(pattern.pattern).startswith('api/'):
            api_patterns.append(str(pattern.pattern))
        elif hasattr(pattern, 'urlconf_name'):
            # Es un include(), verificar si es accounts.api_urls
            if 'api_urls' in getattr(pattern, 'urlconf_name', ''):
                api_patterns.append(f"{pattern.pattern} -> {pattern.urlconf_name}")
    
    for pattern in api_patterns:
        print(f"   - {pattern}")
        
except Exception as e:
    print(f"   ❌ Error verificando URLs: {e}")

# Verificar configuración del proyecto
print(f"\n⚙️ Configuración del proyecto:")
print(f"   DEBUG: {settings.DEBUG}")
print(f"   SECRET_KEY configurado: {'Sí' if settings.SECRET_KEY else 'No'}")
print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")

print(f"\n✅ Diagnóstico completado")
print(f"🌐 Prueba manual en: http://127.0.0.1:8000/api/notifications/list/")
