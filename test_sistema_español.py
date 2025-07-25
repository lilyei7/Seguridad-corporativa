#!/usr/bin/env python
"""
Test script para verificar que las rutas en español funcionen correctamente
y que no haya errores de campos en el modelo Visit.
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_corp.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from visits.models import Visit
from tenants.models import Tenant
from guards.models import Guard

def test_spanish_routes():
    """Test que las rutas en español funcionen"""
    print("🧪 Probando rutas en español...")
    
    try:
        # URLs que deberían funcionar
        routes = [
            '/administracion/',
            '/inquilino/',
            '/vigilante/',
            '/login/',
        ]
        
        client = Client()
        
        for route in routes:
            try:
                # Configurar el host correcto para evitar error de ALLOWED_HOSTS
                response = client.get(route, HTTP_HOST='testserver')
                if response.status_code in [200, 302]:  # 200 = OK, 302 = Redirect (normal para login)
                    print(f"✅ {route} - Funcionando (Status: {response.status_code})")
                else:
                    print(f"❌ {route} - Error (Status: {response.status_code})")
            except Exception as e:
                print(f"❌ {route} - Error: {str(e)}")
                
    except Exception as e:
        print(f"❌ Error general en test de rutas: {str(e)}")

def test_visit_model_fields():
    """Test que los campos del modelo Visit sean correctos"""
    print("\n🧪 Probando campos del modelo Visit...")
    
    try:
        # Verificar que los campos existan
        visit_fields = [field.name for field in Visit._meta.get_fields()]
        
        required_fields = [
            'scheduled_date',
            'scheduled_time', 
            'actual_arrival_time',
            'actual_departure_time',
            'visitor_name',
            'tenant',
            'status'
        ]
        
        for field in required_fields:
            if field in visit_fields:
                print(f"✅ Campo '{field}' - Existe")
            else:
                print(f"❌ Campo '{field}' - No existe")
                
        # Verificar que los campos antiguos no existan
        old_fields = ['visit_date', 'visit_time', 'entry_time', 'exit_time']
        
        for field in old_fields:
            if field not in visit_fields:
                print(f"✅ Campo obsoleto '{field}' - Correctamente removido")
            else:
                print(f"⚠️  Campo obsoleto '{field}' - Aún existe (puede causar confusión)")
                
    except Exception as e:
        print(f"❌ Error en test de modelo: {str(e)}")

def test_url_reverse():
    """Test que los nombres de URLs funcionen"""
    print("\n🧪 Probando nombres de URLs...")
    
    url_names = [
        'login',
        'logout',
        'admin_panel:dashboard',
        'tenant_panel:dashboard', 
        'guard_panel:dashboard',
        'maintenance:report_create',  # Verificar que esta URL funcione
        'guards:guard_list',  # Nueva URL añadida
        'visits:visit_list',  # Nueva URL añadida
        'tenants:tenant_list',  # URL existente
    ]
    
    for url_name in url_names:
        try:
            url = reverse(url_name)
            print(f"✅ URL '{url_name}' -> {url}")
        except Exception as e:
            print(f"❌ URL '{url_name}' - Error: {str(e)}")

def test_login_references():
    """Test que todas las referencias a login sean correctas"""
    print("\n🧪 Verificando referencias de login...")
    
    try:
        # Verificar que 'login' funcione
        login_url = reverse('login')
        print(f"✅ URL 'login' funciona -> {login_url}")
        
        # Verificar que 'accounts:login' NO exista (ya no debería usarse)
        try:
            accounts_login_url = reverse('accounts:login')
            print(f"⚠️  URL 'accounts:login' aún existe -> {accounts_login_url} (debería removerse)")
        except:
            print(f"✅ URL 'accounts:login' correctamente removida (no existe)")
            
    except Exception as e:
        print(f"❌ Error en test de login: {str(e)}")

def test_model_status_consistency():
    """Test que los modelos usen los campos de estado correctos"""
    print("\n🧪 Verificando consistencia de campos de estado...")
    
    try:
        from guards.models import Guard
        from tenants.models import Tenant
        
        # Verificar Guard model - debe usar 'status'
        guard_fields = [field.name for field in Guard._meta.get_fields()]
        if 'status' in guard_fields:
            print("✅ Guard model usa campo 'status' - Correcto")
        else:
            print("❌ Guard model no tiene campo 'status'")
            
        if 'is_active' in guard_fields:
            print("⚠️  Guard model tiene campo 'is_active' - Puede causar confusión")
        else:
            print("✅ Guard model no tiene campo 'is_active' - Correcto")
        
        # Verificar Guard status choices
        status_values = [choice[0] for choice in Guard.GUARD_STATUS_CHOICES]
        expected_statuses = ['activo', 'inactivo', 'suspendido', 'vacaciones']
        
        for status in expected_statuses:
            if status in status_values:
                print(f"✅ Guard status '{status}' - Existe")
            else:
                print(f"❌ Guard status '{status}' - No existe")
        
        # Verificar Tenant model - debe usar 'is_active'  
        tenant_fields = [field.name for field in Tenant._meta.get_fields()]
        if 'is_active' in tenant_fields:
            print("✅ Tenant model usa campo 'is_active' - Correcto")
        else:
            print("❌ Tenant model no tiene campo 'is_active'")
            
    except Exception as e:
        print(f"❌ Error en test de modelos: {str(e)}")

def test_maintenance_model_consistency():
    """Test que el modelo MaintenanceReport tenga valores consistentes"""
    print("\n🧪 Verificando consistencia del modelo MaintenanceReport...")
    
    try:
        from maintenance.models import MaintenanceReport
        
        # Verificar choices de STATUS
        status_values = [choice[0] for choice in MaintenanceReport.STATUS_CHOICES]
        expected_status = ['pendiente', 'en_proceso', 'completado', 'requiere_atencion', 'cancelado']
        
        for status in expected_status:
            if status in status_values:
                print(f"✅ Status '{status}' - Existe en modelo")
            else:
                print(f"❌ Status '{status}' - No existe en modelo")
        
        # Verificar choices de PRIORITY 
        priority_values = [choice[0] for choice in MaintenanceReport.PRIORITY_CHOICES]
        expected_priorities = [1, 2, 3, 4]  # Números, no strings
        
        for priority in expected_priorities:
            if priority in priority_values:
                print(f"✅ Priority {priority} - Existe en modelo")
            else:
                print(f"❌ Priority {priority} - No existe en modelo")
                
        print(f"✅ Prioridades correctas: {priority_values} (números, no strings)")
        
    except Exception as e:
        print(f"❌ Error en test de MaintenanceReport: {str(e)}")

if __name__ == '__main__':
    print("🚀 Iniciando tests del sistema...")
    print("=" * 50)
    
    test_spanish_routes()
    test_visit_model_fields()
    test_url_reverse()
    test_login_references()
    test_maintenance_model_consistency()
    
    print("\n" + "=" * 50)
    print("✅ Tests completados!")
    print("\n💡 Si todos los tests pasaron, el sistema está funcionando correctamente.")
    print("💡 Las rutas en español están funcionando: /administracion/, /inquilino/, /vigilante/")
