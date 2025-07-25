#!/usr/bin/env python
"""
Test rápido para verificar que todos los paneles funcionan correctamente
"""
import os
import sys
import django
from django.test import Client

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_corp.settings')
django.setup()

def test_panels():
    """Test de los paneles separados"""
    print("🧪 Probando paneles con templates separados...")
    
    client = Client()
    
    # URLs a probar
    urls_to_test = [
        ('/administracion/', 'Panel de Administración'),
        ('/inquilino/', 'Portal del Inquilino'), 
        ('/vigilante/', 'Panel de Vigilancia'),
        ('/login/', 'Login')
    ]
    
    for url, name in urls_to_test:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {name} ({url}) - OK")
            elif response.status_code == 302:
                print(f"🔄 {name} ({url}) - Redirección (normal para usuarios no autenticados)")
            else:
                print(f"❌ {name} ({url}) - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {name} ({url}) - Error: {str(e)}")

def test_url_names():
    """Test de nombres de URLs"""
    print("\n🧪 Probando nombres de URLs...")
    
    from django.urls import reverse
    
    urls_to_test = [
        ('login', 'Login'),
        ('admin_panel:dashboard', 'Admin Dashboard'),
        ('tenant_panel:dashboard', 'Tenant Dashboard'),
        ('guard_panel:dashboard', 'Guard Dashboard'),
    ]
    
    for url_name, description in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"✅ {description} -> {url}")
        except Exception as e:
            print(f"❌ {description} - Error: {str(e)}")

if __name__ == '__main__':
    print("🚀 Test de Paneles Separados")
    print("=" * 50)
    
    test_panels()
    test_url_names()
    
    print("\n" + "=" * 50)
    print("✅ Test completado!")
    print("💡 Si no hay errores, todos los paneles están funcionando correctamente")
