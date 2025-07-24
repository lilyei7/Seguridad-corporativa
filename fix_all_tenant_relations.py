#!/usr/bin/env python
"""
Script para corregir TODAS las relaciones usuario-tenant
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_corp.settings')
django.setup()

from django.contrib.auth.models import User
from tenants.models import Tenant

def fix_all_relations():
    print('🔧 Corrigiendo TODAS las relaciones usuario-tenant...')
    print('=' * 60)
    
    # Definir las relaciones correctas basadas en los usuarios existentes
    relations_to_fix = [
        # (username, tenant_name, email)
        ('local1', 'Farmacia San José', 'local101@olcha.com'),
        ('inquilino2', 'Consultorio Dental', 'local205@olcha.com'), 
        ('inquilino_ejemplo', 'Empresa Ejemplo S.A.', 'inquilino@empresaejemplo.com'),
    ]
    
    print(f'📋 Relaciones a corregir: {len(relations_to_fix)}')
    print()
    
    for username, tenant_name, email in relations_to_fix:
        try:
            # Buscar usuario
            user = User.objects.get(username=username)
            print(f'✅ Usuario encontrado: {username}')
            
            # Buscar tenant
            tenant = Tenant.objects.get(tenant_name=tenant_name)
            print(f'✅ Tenant encontrado: {tenant_name}')
            
            # Mostrar estado actual
            print(f'   Estado actual:')
            print(f'     Contact Person: "{tenant.contact_person}"')
            print(f'     Contact Email: {tenant.contact_email}')
            
            # Actualizar relación
            tenant.contact_person = username
            tenant.contact_email = email
            tenant.save()
            
            print(f'   ✅ Actualizado a:')
            print(f'     Contact Person: "{tenant.contact_person}"')
            print(f'     Contact Email: {tenant.contact_email}')
            print()
            
        except User.DoesNotExist:
            print(f'❌ Usuario "{username}" no encontrado')
        except Tenant.DoesNotExist:
            print(f'❌ Tenant "{tenant_name}" no encontrado')
        except Exception as e:
            print(f'❌ Error procesando {username} -> {tenant_name}: {e}')
        print('-' * 40)
    
    # Verificar el resultado final
    print('\n📊 RESULTADO FINAL:')
    print('=' * 60)
    
    for username, tenant_name, email in relations_to_fix:
        try:
            user = User.objects.get(username=username)
            tenant = Tenant.objects.filter(contact_person=username).first()
            
            if tenant and tenant.tenant_name == tenant_name:
                print(f'✅ {username} -> {tenant.tenant_name}')
            else:
                print(f'❌ {username} -> Relación no encontrada o incorrecta')
                if tenant:
                    print(f'   Encontrado: {tenant.tenant_name} (esperado: {tenant_name})')
        except User.DoesNotExist:
            print(f'❌ {username} -> Usuario no existe')
    
    print('\n🎯 VERIFICACIÓN DE ACCESO:')
    print('=' * 60)
    
    # Verificar que cada usuario puede acceder a su tenant
    for username, tenant_name, email in relations_to_fix:
        try:
            user = User.objects.get(username=username)
            
            # Simular la lógica de las vistas de mantenimiento
            tenant = None
            if user.email:
                tenant = Tenant.objects.filter(
                    contact_person=user.username,
                    contact_email=user.email
                ).first()
            
            if not tenant:
                tenant = Tenant.objects.filter(contact_person=user.username).first()
            
            if tenant:
                print(f'✅ {username} puede acceder a: {tenant.tenant_name}')
            else:
                print(f'❌ {username} NO puede acceder a ningún tenant')
                
        except User.DoesNotExist:
            print(f'❌ {username} no existe')

if __name__ == "__main__":
    fix_all_relations()
