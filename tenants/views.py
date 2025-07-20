from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Tenant
from .forms import TenantForm


@login_required
def tenant_create(request):
    """Vista para crear un nuevo inquilino"""
    if request.method == 'POST':
        form = TenantForm(request.POST)
        if form.is_valid():
            tenant = form.save()
            messages.success(request, f'Inquilino {tenant.tenant_name} creado exitosamente')
            return redirect('dashboard:tenants_list')
    else:
        form = TenantForm()
    
    context = {
        'form': form,
        'title': 'Registrar Nuevo Inquilino',
        'button_text': 'Registrar Inquilino'
    }
    
    return render(request, 'tenants/tenant_form_new.html', context)


@login_required
def tenant_detail(request, tenant_id):
    """Vista para ver los detalles de un inquilino"""
    tenant = get_object_or_404(Tenant, id=tenant_id)
    recent_visits = tenant.visit_set.order_by('-scheduled_date')[:10]
    
    context = {
        'tenant': tenant,
        'recent_visits': recent_visits,
    }
    
    return render(request, 'tenants/tenant_detail.html', context)


@login_required
def tenant_edit(request, tenant_id):
    """Vista para editar un inquilino"""
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    if request.method == 'POST':
        form = TenantForm(request.POST, instance=tenant)
        if form.is_valid():
            tenant = form.save()
            messages.success(request, f'Inquilino {tenant.tenant_name} actualizado exitosamente')
            return redirect('tenants:tenant_detail', tenant_id=tenant.id)
    else:
        form = TenantForm(instance=tenant)
    
    context = {
        'form': form,
        'tenant': tenant,
        'title': f'Editar Inquilino: {tenant.tenant_name}',
        'button_text': 'Actualizar Inquilino'
    }
    
    return render(request, 'tenants/tenant_form_new.html', context)


@login_required
@require_http_methods(["DELETE"])
def tenant_delete(request, tenant_id):
    """Vista para eliminar un inquilino (AJAX)"""
    try:
        tenant = get_object_or_404(Tenant, id=tenant_id)
        
        # Verificar si el inquilino tiene visitas activas
        active_visits = tenant.visit_set.filter(status='pending').count()
        if active_visits > 0:
            return JsonResponse({
                'success': False,
                'message': f'No se puede eliminar el inquilino. Tiene {active_visits} visitas pendientes.'
            })
        
        tenant_name = tenant.tenant_name
        tenant.delete()
        
        messages.success(request, f'Inquilino {tenant_name} eliminado exitosamente')
        return JsonResponse({
            'success': True,
            'message': f'Inquilino {tenant_name} eliminado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar inquilino: {str(e)}'
        })


@login_required
def tenant_list(request):
    """Vista para listar todos los inquilinos"""
    tenants = Tenant.objects.filter(is_active=True).order_by('tenant_name')
    
    # Filtros
    search = request.GET.get('search', '')
    if search:
        tenants = tenants.filter(tenant_name__icontains=search)
    
    context = {
        'tenants': tenants,
        'search': search,
    }
    
    return render(request, 'tenants/tenant_list.html', context)
