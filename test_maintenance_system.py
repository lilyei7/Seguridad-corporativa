#!/usr/bin/env python
"""
Script de verificación final para el sistema de mantenimiento
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_corp.settings')
django.setup()

from django.contrib.auth.models import User
from tenants.models import Tenant
from maintenance.models import MaintenanceRequest

def test_system():
    print('🔍 VERIFICACIÓN FINAL DEL SISTEMA DE MANTENIMIENTO')
    print('=' * 60)
    
    # Usuarios de prueba
    test_users = ['local1', 'inquilino2', 'inquilino_ejemplo']
    
    for username in test_users:
        try:
            print(f'\n👤 Probando usuario: {username}')
            print('-' * 30)
            
            user = User.objects.get(username=username)
            print(f'✅ Usuario encontrado: {user.username} ({user.email})')
            
            # Buscar tenant
            tenant = None
            search_methods = []
            
            # Método 1: Por usuario y email
            if user.email:
                tenant = Tenant.objects.filter(
                    contact_person=user.username,
                    contact_email=user.email
                ).first()
                if tenant:
                    search_methods.append('usuario+email')
            
            # Método 2: Solo por usuario
            if not tenant:
                tenant = Tenant.objects.filter(contact_person=user.username).first()
                if tenant:
                    search_methods.append('solo_usuario')
            
            if tenant:
                print(f'✅ Tenant encontrado: {tenant.tenant_name} (método: {search_methods[0]})')
                
                # Verificar solicitudes
                requests = MaintenanceRequest.objects.filter(tenant=tenant)
                print(f'📋 Solicitudes de mantenimiento: {requests.count()}')
                
                if requests.exists():
                    print('   Solicitudes:')
                    for req in requests:
                        status_icons = {
                            'pendiente': '⏳',
                            'en_revision': '👁️',
                            'en_proceso': '🔧', 
                            'completada': '✅',
                            'urgente': '🚨'
                        }
                        icon = status_icons.get(req.urgency_level, status_icons.get(req.status, '📝'))
                        print(f'   {icon} {req.title} ({req.get_status_display()})')
                
                print('✅ Sistema FUNCIONANDO correctamente')
            else:
                print('❌ No se encontró tenant asociado')
                
        except User.DoesNotExist:
            print(f'❌ Usuario {username} no encontrado')
        except Exception as e:
            print(f'❌ Error: {e}')
    
    print(f'\n📊 RESUMEN GENERAL')
    print('=' * 60)
    total_tenants = Tenant.objects.count()
    total_users = User.objects.count()
    total_requests = MaintenanceRequest.objects.count()
    
    print(f'👥 Total usuarios: {total_users}')
    print(f'🏢 Total tenants: {total_tenants}') 
    print(f'📋 Total solicitudes: {total_requests}')
    
    print(f'\n🎯 URLS DE PRUEBA')
    print('=' * 60)
    print('Solicitar mantenimiento: http://127.0.0.1:8000/maintenance/request/')
    print('Mis solicitudes: http://127.0.0.1:8000/maintenance/my-requests/')
    print('Panel inquilino: http://127.0.0.1:8000/dashboard/tenant/')
    
    print(f'\n👤 CREDENCIALES DE PRUEBA')
    print('=' * 60)
    for username in test_users:
        print(f'• Usuario: {username} | Contraseña: [usar la que está configurada]')

if __name__ == "__main__":
    test_system()
