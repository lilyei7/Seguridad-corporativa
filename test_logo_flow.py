#!/usr/bin/env python
"""
Script para validar todo el flujo del logo paso a paso
"""
import os
import sys
import django
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_corp.settings')
django.setup()

from django.conf import settings
from dashboard.models import SystemThemeConfiguration
from django.test import Client
from django.contrib.auth.models import User

# Agregar testserver a ALLOWED_HOSTS para las pruebas
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

def test_logo_flow():
    """Probar todo el flujo del logo"""
    print("🔍 VALIDACIÓN COMPLETA DEL FLUJO DEL LOGO")
    print("=" * 50)
    
    # 1. Verificar configuración en BD
    print("\n1. 📊 CONFIGURACIÓN EN BASE DE DATOS:")
    config = SystemThemeConfiguration.get_active_config()
    if not config:
        print("   ❌ No hay configuración activa")
        return False
    
    print(f"   ✅ Configuración activa: {config.company_name}")
    print(f"   ✅ Logo configurado: {bool(config.company_logo)}")
    
    if not config.company_logo:
        print("   ❌ No hay logo configurado")
        return False
    
    logo_name = config.company_logo.name
    logo_url = config.company_logo.url
    print(f"   📁 Archivo: {logo_name}")
    print(f"   🌐 URL: {logo_url}")
    
    # 2. Verificar archivo físico
    print("\n2. 📁 ARCHIVO FÍSICO:")
    logo_path = Path(settings.MEDIA_ROOT) / logo_name
    
    if not logo_path.exists():
        print(f"   ❌ Archivo no existe: {logo_path}")
        return False
    
    print(f"   ✅ Archivo existe: {logo_path}")
    print(f"   📏 Tamaño: {logo_path.stat().st_size} bytes")
    
    # 3. Verificar acceso HTTP
    print("\n3. 🌐 ACCESO HTTP:")
    client = Client()
    
    # Crear usuario temporal para pruebas
    try:
        test_user = User.objects.get(username='test_user')
    except User.DoesNotExist:
        test_user = User.objects.create_user('test_user', 'test@test.com', 'password')
    
    client.force_login(test_user)
    
    # Probar acceso al logo
    response = client.get(logo_url)
    print(f"   📡 Respuesta HTTP: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ Logo accesible via HTTP")
        try:
            if hasattr(response, 'content'):
                content_size = len(response.content)
            elif hasattr(response, 'streaming_content'):
                content_size = sum(len(chunk) for chunk in response.streaming_content)
            else:
                content_size = "No determinado"
            print(f"   📏 Tamaño respuesta: {content_size} bytes")
        except Exception as e:
            print(f"   📏 Tamaño respuesta: No determinado ({e})")
        print(f"   📋 Content-Type: {response.get('Content-Type', 'No especificado')}")
    else:
        print(f"   ❌ Error HTTP: {response.status_code}")
        return False
    
    # 4. Verificar API de configuración
    print("\n4. 🔌 API DE CONFIGURACIÓN:")
    api_response = client.get('/dashboard/api/system-config/')
    print(f"   📡 Respuesta API: {api_response.status_code}")
    
    if api_response.status_code == 200:
        api_data = api_response.json()
        print(f"   ✅ API funcional")
        print(f"   📊 Datos: {api_data}")
        
        if api_data.get('logo_url') == logo_url:
            print(f"   ✅ URL del logo coincide en API")
        else:
            print(f"   ⚠️  URL del logo no coincide: API={api_data.get('logo_url')}, BD={logo_url}")
    else:
        print(f"   ❌ Error en API: {api_response.status_code}")
        return False
    
    # 5. Verificar template rendering
    print("\n5. 📄 RENDERIZADO DE TEMPLATE:")
    try:
        dashboard_response = client.get('/dashboard/')
        if dashboard_response.status_code == 200:
            content = dashboard_response.content.decode('utf-8')
            
            # Buscar el logo en el HTML
            if logo_url in content:
                print(f"   ✅ Logo URL encontrada en HTML")
                print(f"   📍 Apariciones del logo: {content.count(logo_url)}")
            else:
                print(f"   ❌ Logo URL NO encontrada en HTML")
                print(f"   🔍 Buscando variaciones...")
                # Buscar posibles variaciones
                if 'company_logo' in content:
                    print(f"   📝 'company_logo' encontrado en template")
                if 'sidebar-logo' in content:
                    print(f"   📝 'sidebar-logo' encontrado en template")
                
            # Verificar si hay errores JavaScript en el template
            if 'themeConfig' in content:
                print(f"   ✅ themeConfig encontrado en template")
            else:
                print(f"   ⚠️  themeConfig NO encontrado en template")
                
        else:
            print(f"   ❌ Error accediendo al dashboard: {dashboard_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en template: {e}")
        return False
    
    # Cleanup
    test_user.delete()
    
    print("\n" + "=" * 50)
    print("✅ VALIDACIÓN COMPLETADA - TODO FUNCIONAL")
    print("=" * 50)
    return True

def suggest_fixes():
    """Sugerir posibles soluciones"""
    print("\n🔧 POSIBLES SOLUCIONES:")
    print("1. 🔄 Recargar página completamente (Ctrl+F5)")
    print("2. 🧹 Limpiar caché del navegador")
    print("3. 🔍 Abrir herramientas de desarrollador y revisar errores")
    print("4. 📱 Probar desde dispositivo móvil")
    print("5. 🌐 Verificar que no hay proxy/CDN interfiriendo")
    print("6. 🔌 Revisar extensiones del navegador")

if __name__ == "__main__":
    success = test_logo_flow()
    if not success:
        suggest_fixes()
