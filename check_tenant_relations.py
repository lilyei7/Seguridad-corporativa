#!/usr/bin/env python
"""
Script para verificar relaciones usuario-tenant
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_corp.settings')
django.setup()

from django.contrib.auth.models import User
from tenants.models import Tenant

print('🔍 Verificando relaciones usuario-tenant actuales...')

# Ver todos los tenants y sus contactos
tenants = Tenant.objects.all()
print(f'Total tenants: {tenants.count()}')
print()

for tenant in tenants:
    print(f'Tenant: {tenant.tenant_name}')
    print(f'  Contact Person: "{tenant.contact_person}"')
    print(f'  Contact Email: {tenant.contact_email}')
    print()

# Ver el usuario inquilino_ejemplo
try:
    user = User.objects.get(username='inquilino_ejemplo')
    print(f'✅ Usuario encontrado: {user.username}')
    print(f'   Email: {user.email}')
    print()
    
    # Probar diferentes formas de buscar
    print('🔍 Probando diferentes búsquedas:')
    
    # Búsqueda exacta
    exact_match = Tenant.objects.filter(contact_person=user.username).first()
    print(f'1. Búsqueda exacta (contact_person="{user.username}"): {exact_match}')
    
    # Búsqueda con icontains
    icontains_match = Tenant.objects.filter(contact_person__icontains=user.username).first()
    print(f'2. Búsqueda icontains: {icontains_match}')
    
    # Búsqueda por email
    email_match = Tenant.objects.filter(contact_email=user.email).first()
    print(f'3. Búsqueda por email ({user.email}): {email_match}')
    
    print()
    print('🔧 Vamos a arreglar la relación:')
    
    # Encontrar el tenant correcto
    target_tenant = Tenant.objects.filter(tenant_name='Empresa Ejemplo S.A.').first()
    if target_tenant:
        print(f'Tenant objetivo: {target_tenant.tenant_name}')
        print(f'Contact actual: "{target_tenant.contact_person}"')
        
        # Actualizar la relación
        target_tenant.contact_person = user.username
        target_tenant.contact_email = user.email
        target_tenant.save()
        
        print(f'✅ Relación actualizada:')
        print(f'   Usuario: {user.username}')
        print(f'   Tenant: {target_tenant.tenant_name}')
        print(f'   Contact Person: "{target_tenant.contact_person}"')
    else:
        print('❌ No se encontró el tenant "Empresa Ejemplo S.A."')
    
except User.DoesNotExist:
    print('❌ Usuario inquilino_ejemplo no encontrado')
except Exception as e:
    print(f'❌ Error: {e}')
