from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.utils import timezone
from tenants.models import Tenant
from guards.models import Guard
from visits.models import Visit
from maintenance.models import MaintenanceReport
from datetime import date, timedelta
from django.db.models import Q, Count

User = get_user_model()

# =====================================================
# VISTAS MÓVILES PARA INQUILINOS
# =====================================================

@method_decorator(login_required, name='dispatch')
class TenantMobileDashboard(TemplateView):
    template_name = 'mobile_app/tenant/dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar que sea inquilino
        if not hasattr(request.user, 'tenant'):
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        tenant = user.tenant
        
        # Estadísticas del inquilino
        today = date.today()
        context.update({
            'tenant': tenant,
            'visits_today': Visit.objects.filter(
                tenant=tenant,
                scheduled_date=today
            ).count(),
            'visits_pending': Visit.objects.filter(
                tenant=tenant,
                status='pendiente'
            ).count(),
            'maintenance_pending': MaintenanceReport.objects.filter(
                tenant=tenant,
                status__in=['pendiente', 'en_proceso']
            ).count(),
            'upcoming_visits': Visit.objects.filter(
                tenant=tenant,
                scheduled_date__gte=today,
                status__in=['aprobada', 'pendiente']
            ).order_by('scheduled_date', 'scheduled_time')[:5],
        })
        return context

@login_required
def tenant_mobile_visits(request):
    """Vista móvil para gestión de visitas de inquilino"""
    if not hasattr(request.user, 'tenant'):
        return redirect('login')
    
    tenant = request.user.tenant
    visits = Visit.objects.filter(tenant=tenant).order_by('-scheduled_date')
    
    context = {
        'visits': visits,
        'tenant': tenant,
    }
    return render(request, 'mobile_app/tenant/visits.html', context)

@login_required
def tenant_mobile_request_visit(request):
    """Vista móvil para solicitar visita"""
    if not hasattr(request.user, 'tenant'):
        return redirect('login')
    
    if request.method == 'POST':
        # Procesar solicitud de visita
        tenant = request.user.tenant
        visit = Visit.objects.create(
            tenant=tenant,
            visitor_name=request.POST.get('visitor_name'),
            visitor_phone=request.POST.get('visitor_phone', ''),
            scheduled_date=request.POST.get('scheduled_date'),
            scheduled_time=request.POST.get('scheduled_time'),
            purpose=request.POST.get('purpose', ''),
            status='pendiente'
        )
        return JsonResponse({'success': True, 'visit_id': visit.id})
    
    context = {
        'tenant': request.user.tenant,
    }
    return render(request, 'mobile_app/tenant/request_visit.html', context)

# =====================================================
# VISTAS MÓVILES PARA VIGILANTES
# =====================================================

@method_decorator(login_required, name='dispatch')
class GuardMobileDashboard(TemplateView):
    template_name = 'mobile_app/guard/dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar que sea vigilante
        try:
            guard = Guard.objects.get(user=request.user)
            if guard.status != 'activo':
                return redirect('login')
        except Guard.DoesNotExist:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        guard = Guard.objects.get(user=user)
        today = date.today()
        
        context.update({
            'guard': guard,
            'visits_today': Visit.objects.filter(
                scheduled_date=today,
                status__in=['aprobada', 'en_espera']
            ).count(),
            'visits_pending_approval': Visit.objects.filter(
                status='pendiente'
            ).count(),
            'visitors_in_building': Visit.objects.filter(
                status='en_curso',
                scheduled_date=today
            ).count(),
            'pending_visits': Visit.objects.filter(
                status='pendiente'
            ).order_by('scheduled_date', 'scheduled_time')[:10],
            'todays_visits': Visit.objects.filter(
                scheduled_date=today,
                status__in=['aprobada', 'en_espera', 'en_curso']
            ).order_by('scheduled_time'),
        })
        return context

@login_required
def guard_mobile_scanner(request):
    """Vista móvil para scanner QR de vigilante"""
    try:
        guard = Guard.objects.get(user=request.user)
        if guard.status != 'activo':
            return redirect('login')
    except Guard.DoesNotExist:
        return redirect('login')
    
    context = {
        'guard': guard,
    }
    return render(request, 'mobile_app/guard/scanner.html', context)

@login_required
def guard_mobile_visits(request):
    """Vista móvil para gestión de visitas del vigilante"""
    try:
        guard = Guard.objects.get(user=request.user)
        if guard.status != 'activo':
            return redirect('login')
    except Guard.DoesNotExist:
        return redirect('login')
    
    today = date.today()
    visits = Visit.objects.filter(
        Q(scheduled_date=today) | Q(status='pendiente')
    ).order_by('scheduled_date', 'scheduled_time')
    
    context = {
        'guard': guard,
        'visits': visits,
    }
    return render(request, 'mobile_app/guard/visits.html', context)

# =====================================================
# VISTAS MÓVILES PARA ADMINISTRADORES
# =====================================================

@method_decorator(login_required, name='dispatch')
class AdminMobileDashboard(TemplateView):
    template_name = 'mobile_app/admin/dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar que sea admin
        if not (request.user.is_staff or request.user.is_superuser):
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        
        # Estadísticas generales
        context.update({
            'total_tenants': Tenant.objects.filter(is_active=True).count(),
            'total_guards': Guard.objects.filter(status='activo').count(),
            'visits_today': Visit.objects.filter(scheduled_date=today).count(),
            'maintenance_pending': MaintenanceReport.objects.filter(
                status__in=['pendiente', 'en_proceso']
            ).count(),
            'recent_visits': Visit.objects.filter(
                scheduled_date__gte=today - timedelta(days=7)
            ).order_by('-scheduled_date', '-scheduled_time')[:10],
            'urgent_maintenance': MaintenanceReport.objects.filter(
                priority__in=[1, 2],
                status__in=['pendiente', 'en_proceso']
            ).order_by('priority', 'created_at')[:5],
        })
        return context

@login_required
def admin_mobile_live_monitor(request):
    """Vista móvil para monitoreo en vivo"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('login')
    
    today = date.today()
    context = {
        'active_visits': Visit.objects.filter(
            status='en_curso',
            scheduled_date=today
        ).order_by('actual_arrival_time'),
        'pending_approvals': Visit.objects.filter(
            status='pendiente'
        ).order_by('scheduled_date', 'scheduled_time'),
        'guards_on_duty': Guard.objects.filter(
            status='activo'
        ).order_by('user__first_name'),
    }
    return render(request, 'mobile_app/admin/live_monitor.html', context)

# =====================================================
# API ENDPOINTS PARA FUNCIONES MÓVILES
# =====================================================

@login_required
def mobile_api_approve_visit(request, visit_id):
    """API para aprobar visita desde móvil"""
    if request.method == 'POST':
        try:
            # Verificar permisos (vigilante o admin)
            is_guard = Guard.objects.filter(user=request.user, status='activo').exists()
            is_admin = request.user.is_staff or request.user.is_superuser
            
            if not (is_guard or is_admin):
                return JsonResponse({'success': False, 'error': 'Sin permisos'})
            
            visit = Visit.objects.get(id=visit_id)
            visit.status = 'aprobada'
            visit.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Visita aprobada exitosamente'
            })
        except Visit.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Visita no encontrada'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def mobile_api_register_entry(request, visit_id):
    """API para registrar entrada desde móvil"""
    if request.method == 'POST':
        try:
            # Solo vigilantes pueden registrar entradas
            guard = Guard.objects.get(user=request.user, status='activo')
            
            visit = Visit.objects.get(id=visit_id)
            visit.status = 'en_curso'
            visit.actual_arrival_time = timezone.now().time()
            visit.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Entrada registrada exitosamente'
            })
        except (Guard.DoesNotExist, Visit.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Error en el registro'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
