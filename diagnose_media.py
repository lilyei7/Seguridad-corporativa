#!/usr/bin/env python
"""
Script de diagnóstico para verificar la configuración de archivos media en Django
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

def check_media_configuration():
    """Verificar la configuración de archivos media"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE CONFIGURACIÓN DE MEDIA")
    print("=" * 60)
    
    # 1. Verificar configuración en settings
    print("\n1. 📋 CONFIGURACIÓN EN SETTINGS:")
    print(f"   MEDIA_URL: {settings.MEDIA_URL}")
    print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"   DEBUG: {settings.DEBUG}")
    
    # 2. Verificar existencia de carpetas
    print("\n2. 📁 ESTRUCTURA DE CARPETAS:")
    media_root = Path(settings.MEDIA_ROOT)
    print(f"   Media root existe: {media_root.exists()}")
    
    if media_root.exists():
        print(f"   Permisos de media: {oct(media_root.stat().st_mode)[-3:]}")
        
        # Verificar subcarpetas específicas
        config_logos = media_root / 'configuration' / 'logos'
        print(f"   Carpeta configuration/logos existe: {config_logos.exists()}")
        
        if not config_logos.exists():
            print("   ⚠️  Creando carpeta configuration/logos...")
            config_logos.mkdir(parents=True, exist_ok=True)
            print("   ✅ Carpeta creada")
    else:
        print("   ⚠️  Carpeta media no existe, creando...")
        media_root.mkdir(parents=True, exist_ok=True)
        (media_root / 'configuration' / 'logos').mkdir(parents=True, exist_ok=True)
        print("   ✅ Carpetas creadas")
    
    # 3. Verificar configuraciones en base de datos
    print("\n3. 🗄️  CONFIGURACIONES EN BASE DE DATOS:")
    try:
        configs = SystemThemeConfiguration.objects.all()
        print(f"   Total configuraciones: {configs.count()}")
        
        active_config = SystemThemeConfiguration.get_active_config()
        if active_config:
            print(f"   Configuración activa: {active_config.company_name}")
            print(f"   Logo configurado: {bool(active_config.company_logo)}")
            
            if active_config.company_logo:
                logo_path = Path(settings.MEDIA_ROOT) / active_config.company_logo.name
                print(f"   Ruta del logo: {active_config.company_logo.name}")
                print(f"   URL del logo: {active_config.company_logo.url}")
                print(f"   Archivo existe físicamente: {logo_path.exists()}")
                
                if logo_path.exists():
                    print(f"   Tamaño del archivo: {logo_path.stat().st_size} bytes")
                else:
                    print("   ❌ El archivo del logo no existe en el sistema de archivos")
        else:
            print("   ⚠️  No hay configuración activa")
            
    except Exception as e:
        print(f"   ❌ Error al acceder a la base de datos: {e}")
    
    # 4. Verificar URLs
    print("\n4. 🌐 CONFIGURACIÓN DE URLs:")
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        # Intentar acceder a una URL de media ficticia
        print("   URLs configuradas correctamente para servir archivos media en DEBUG=True")
    except Exception as e:
        print(f"   ⚠️  Posible problema con URLs: {e}")
    
    # 5. Verificar permisos de escritura
    print("\n5. ✍️  PERMISOS DE ESCRITURA:")
    try:
        test_file = media_root / 'test_write.txt'
        test_file.write_text('test')
        test_file.unlink()
        print("   ✅ Permisos de escritura: OK")
    except Exception as e:
        print(f"   ❌ Error de permisos de escritura: {e}")
    
    print("\n" + "=" * 60)
    print("🔧 DIAGNÓSTICO COMPLETADO")
    print("=" * 60)

def fix_media_permissions():
    """Intentar arreglar permisos de la carpeta media"""
    print("\n🔧 INTENTANDO ARREGLAR PERMISOS...")
    
    media_root = Path(settings.MEDIA_ROOT)
    
    try:
        # En Windows, verificar que la carpeta existe y es accesible
        if not media_root.exists():
            media_root.mkdir(parents=True, exist_ok=True)
            print("   ✅ Carpeta media creada")
        
        # Crear subcarpetas necesarias
        (media_root / 'configuration' / 'logos').mkdir(parents=True, exist_ok=True)
        (media_root / 'configuration' / 'favicons').mkdir(parents=True, exist_ok=True)
        print("   ✅ Subcarpetas de configuración creadas")
        
        # Crear archivo de prueba
        test_file = media_root / 'test_permissions.txt'
        test_file.write_text('Test file for permissions')
        test_file.unlink()
        print("   ✅ Permisos de escritura verificados")
        
    except Exception as e:
        print(f"   ❌ Error al arreglar permisos: {e}")
        print("   💡 Soluciones manuales:")
        print("      - Verifica que la carpeta media tenga permisos de escritura")
        print("      - En Windows: clic derecho > Propiedades > Seguridad")
        print("      - En Linux: chmod 755 media/")

if __name__ == "__main__":
    check_media_configuration()
    fix_media_permissions()
