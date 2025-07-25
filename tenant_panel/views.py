from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, CreateView
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from tenants.models import Tenant
from visits.models import Visit
from maintenance.models import MaintenanceReport
from visits.forms import VisitForm


class TenantPanelMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin para verificar que el usuario sea un inquilino"""
    
    def test_func(self):
        try:
            # Verificar si el usuario tiene un inquilino asociado
            tenant = Tenant.objects.get(assigned_user=self.request.user)
            return tenant.is_active
        except Tenant.DoesNotExist:
            return False
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes acceso al panel de inquilinos o tu cuenta está inactiva.')
        return redirect('login')
    
    def get_tenant(self):
        """Obtiene el inquilino asociado al usuario actual"""
        return get_object_or_404(Tenant, assigned_user=self.request.user)


class TenantDashboardView(TenantPanelMixin, TemplateView):
    """Vista principal del panel de inquilinos"""
    template_name = 'tenant_panel/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.get_tenant()
        
        # Estadísticas del inquilino
        context.update({
            'tenant': tenant,
            'my_visits_today': Visit.objects.filter(
                tenant=tenant,
                created_at__date=timezone.now().date()
            ).count(),
            'pending_visits': Visit.objects.filter(
                tenant=tenant,
                status='pending'
            ).count(),
            'approved_visits': Visit.objects.filter(
                tenant=tenant,
                status='approved'
            ).count(),
        })
        
        # Visitas recientes
        context['recent_visits'] = Visit.objects.filter(
            tenant=tenant
        ).order_by('-created_at')[:5]
        
        # Próximas visitas aprobadas
        context['upcoming_visits'] = Visit.objects.filter(
            tenant=tenant,
            status='approved',
            scheduled_date__gte=timezone.now().date()
        ).order_by('scheduled_date', 'scheduled_time')[:5]
        
        # Reportes de mantenimiento del inquilino
        context['my_maintenance_reports'] = MaintenanceReport.objects.filter(
            reported_by=self.request.user
        ).order_by('-created_at')[:3]
        
        return context


class TenantVisitsView(TenantPanelMixin, ListView):
    """Vista para listar las visitas del inquilino"""
    template_name = 'tenant_panel/visits.html'
    context_object_name = 'visits'
    paginate_by = 10
    
    def get_queryset(self):
        tenant = self.get_tenant()
        queryset = Visit.objects.filter(tenant=tenant).order_by('-created_at')
        
        # Filtros opcionales
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(visitor_name__icontains=search) |
                Q(visitor_id__icontains=search) |
                Q(purpose__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tenant'] = self.get_tenant()
        context['status_choices'] = Visit.STATUS_CHOICES
        return context


@login_required
def tenant_create_visit(request):
    """Vista para crear una nueva visita"""
    try:
        tenant = Tenant.objects.get(assigned_user=request.user)
        if not tenant.is_active:
            messages.error(request, 'Tu cuenta de inquilino está inactiva.')
            return redirect('login')
    except Tenant.DoesNotExist:
        messages.error(request, 'No tienes acceso al panel de inquilinos.')
        return redirect('login')
    
    if request.method == 'POST':
        form = VisitForm(request.POST, request.FILES)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.tenant = tenant
            visit.save()
            messages.success(request, 'Visita registrada exitosamente. Pendiente de aprobación.')
            return redirect('tenant_panel:visits')
    else:
        form = VisitForm()
    
    context = {
        'form': form,
        'tenant': tenant,
    }
    return render(request, 'tenant_panel/create_visit.html', context)


@login_required
def tenant_visit_detail(request, visit_id):
    """Vista para ver detalle de una visita"""
    try:
        tenant = Tenant.objects.get(assigned_user=request.user)
    except Tenant.DoesNotExist:
        messages.error(request, 'No tienes acceso al panel de inquilinos.')
        return redirect('login')
    
    visit = get_object_or_404(Visit, id=visit_id, tenant=tenant)
    
    context = {
        'visit': visit,
        'tenant': tenant,
    }
    return render(request, 'tenant_panel/visit_detail.html', context)


@login_required
def tenant_maintenance_view(request):
    """Vista para reportes de mantenimiento del inquilino"""
    try:
        tenant = Tenant.objects.get(assigned_user=request.user)
    except Tenant.DoesNotExist:
        messages.error(request, 'No tienes acceso al panel de inquilinos.')
        return redirect('login')
    
    # Reportes del inquilino
    reports = MaintenanceReport.objects.filter(
        reported_by=request.user
    ).order_by('-created_at')
    
    context = {
        'tenant': tenant,
        'reports': reports,
        'pending_reports': reports.filter(status='pendiente').count(),
        'in_progress_reports': reports.filter(status='en_proceso').count(),
        'completed_reports': reports.filter(status='completado').count(),
    }
    return render(request, 'tenant_panel/maintenance.html', context)


@login_required
def tenant_profile_view(request):
    """Vista para el perfil del inquilino"""
    try:
        tenant = Tenant.objects.get(assigned_user=request.user)
    except Tenant.DoesNotExist:
        messages.error(request, 'No tienes acceso al panel de inquilinos.')
        return redirect('login')
    
    context = {
        'tenant': tenant,
    }
    return render(request, 'tenant_panel/profile.html', context)
