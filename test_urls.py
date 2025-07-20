#!/usr/bin/env python3
"""
Script para verificar que todas las URLs principales funcionen correctamente
"""

import requests
import sys

# URLs principales a verificar
urls_to_test = [
    'http://127.0.0.1:8000/',  # Login
    'http://127.0.0.1:8000/dashboard/',  # Dashboard principal
    'http://127.0.0.1:8000/dashboard/admin/',  # Panel admin
    'http://127.0.0.1:8000/dashboard/my-shift/',  # Mi turno
    'http://127.0.0.1:8000/dashboard/visits/',  # Lista de visitas
    'http://127.0.0.1:8000/dashboard/tenants/',  # Lista de inquilinos
    'http://127.0.0.1:8000/dashboard/guards/',  # Lista de guardias
    'http://127.0.0.1:8000/maintenance/',  # Mantenimiento
]

def test_urls():
    """Probar todas las URLs"""
    print("🔍 Verificando URLs del sistema...")
    print("-" * 50)
    
    failed_urls = []
    
    for url in urls_to_test:
        try:
            response = requests.get(url, timeout=5, allow_redirects=True)
            if response.status_code in [200, 302]:  # 200 OK o 302 Redirect están bien
                print(f"✅ {url} - OK ({response.status_code})")
            else:
                print(f"❌ {url} - ERROR ({response.status_code})")
                failed_urls.append(url)
        except requests.exceptions.RequestException as e:
            print(f"❌ {url} - CONEXIÓN ERROR: {e}")
            failed_urls.append(url)
    
    print("-" * 50)
    if failed_urls:
        print(f"❌ {len(failed_urls)} URLs fallaron:")
        for url in failed_urls:
            print(f"   - {url}")
        return False
    else:
        print("✅ Todas las URLs funcionan correctamente!")
        return True

if __name__ == "__main__":
    success = test_urls()
    sys.exit(0 if success else 1)
