from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse

from guards.models import Guard
from visits.models import Visit
from tenants.models import Tenant
from maintenance.models import MaintenanceReport


class GuardPanelMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin para verificar que el usuario sea un vigilante"""
    
    def test_func(self):
        try:
            # Verificar si el usuario tiene un vigilante asociado
            guard = Guard.objects.get(user=self.request.user)
            return guard.status == 'activo'
        except Guard.DoesNotExist:
            return False
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes acceso al panel de vigilantes o tu cuenta está inactiva.')
        return redirect('login')
    
    def get_guard(self):
        """Obtiene el vigilante asociado al usuario actual"""
        return get_object_or_404(Guard, user=self.request.user)


class GuardDashboardView(GuardPanelMixin, TemplateView):
    """Vista principal del panel de vigilantes"""
    template_name = 'guard_panel/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        guard = self.get_guard()
        today = timezone.now().date()
        
        # Estadísticas del vigilante
        context.update({
            'guard': guard,
            'visits_today': Visit.objects.filter(
                created_at__date=today
            ).count(),
            'pending_approvals': Visit.objects.filter(
                status='pending'
            ).count(),
            'active_visits': Visit.objects.filter(
                status='approved',
                scheduled_date=today
            ).count(),
        })
        
        # Visitas pendientes de aprobación
        context['pending_visits'] = Visit.objects.filter(
            status='pending'
        ).select_related('tenant').order_by('-created_at')[:10]
        
        # Visitas de hoy
        context['todays_visits'] = Visit.objects.filter(
            scheduled_date=today,
            status__in=['approved', 'completed']
        ).select_related('tenant').order_by('scheduled_time')
        
        # Visitantes actualmente en el edificio
        context['active_visitors'] = Visit.objects.filter(
            status='approved',
            scheduled_date=today,
            actual_arrival_time__isnull=False,
            actual_departure_time__isnull=True
        ).select_related('tenant')
        
        return context


class GuardVisitsView(GuardPanelMixin, ListView):
    """Vista para gestionar visitas"""
    template_name = 'guard_panel/visits.html'
    context_object_name = 'visits'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Visit.objects.select_related('tenant').order_by('-created_at')
        
        # Filtros
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        date_filter = self.request.GET.get('date')
        if date_filter:
            if date_filter == 'today':
                queryset = queryset.filter(scheduled_date=timezone.now().date())
            elif date_filter == 'tomorrow':
                tomorrow = timezone.now().date() + timedelta(days=1)
                queryset = queryset.filter(scheduled_date=tomorrow)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(visitor_name__icontains=search) |
                Q(visitor_id__icontains=search) |
                Q(tenant__unit_number__icontains=search) |
                Q(tenant__assigned_user__first_name__icontains=search) |
                Q(tenant__assigned_user__last_name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guard'] = self.get_guard()
        context['status_choices'] = Visit.STATUS_CHOICES
        return context


@login_required
def guard_approve_visit(request, visit_id):
    """Vista para aprobar una visita"""
    try:
        guard = Guard.objects.get(user=request.user)
        if guard.status != 'activo':
            return JsonResponse({'success': False, 'error': 'Cuenta de vigilante inactiva'})
    except Guard.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No tienes acceso al panel de vigilantes'})
    
    visit = get_object_or_404(Visit, id=visit_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            visit.status = 'approved'
            visit.approved_by = request.user
            visit.approved_at = timezone.now()
            visit.save()
            
            messages.success(request, f'Visita de {visit.visitor_name} aprobada exitosamente.')
            return JsonResponse({'success': True, 'message': 'Visita aprobada'})
            
        elif action == 'reject':
            rejection_reason = request.POST.get('rejection_reason', '')
            visit.status = 'cancelled'
            visit.rejection_reason = rejection_reason
            visit.save()
            
            messages.success(request, f'Visita de {visit.visitor_name} rechazada.')
            return JsonResponse({'success': True, 'message': 'Visita rechazada'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def guard_register_entry(request, visit_id):
    """Vista para registrar entrada de visitante"""
    try:
        guard = Guard.objects.get(user=request.user)
    except Guard.DoesNotExist:
        messages.error(request, 'No tienes acceso al panel de vigilantes.')
        return redirect('login')
    
    visit = get_object_or_404(Visit, id=visit_id, status='approved')
    
    if request.method == 'POST':
        visit.entry_time = timezone.now()
        visit.entry_guard = guard
        visit.save()
        
        messages.success(request, f'Entrada registrada para {visit.visitor_name}.')
        return JsonResponse({'success': True, 'message': 'Entrada registrada'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def guard_register_exit(request, visit_id):
    """Vista para registrar salida de visitante"""
    try:
        guard = Guard.objects.get(user=request.user)
    except Guard.DoesNotExist:
        messages.error(request, 'No tienes acceso al panel de vigilantes.')
        return redirect('login')
    
    visit = get_object_or_404(Visit, id=visit_id, entry_time__isnull=False, exit_time__isnull=True)
    
    if request.method == 'POST':
        visit.exit_time = timezone.now()
        visit.exit_guard = guard
        visit.status = 'completed'
        visit.save()
        
        messages.success(request, f'Salida registrada para {visit.visitor_name}.')
        return JsonResponse({'success': True, 'message': 'Salida registrada'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def guard_tenants_view(request):
    """Vista para ver información de inquilinos"""
    try:
        guard = Guard.objects.get(user=request.user)
    except Guard.DoesNotExist:
        messages.error(request, 'No tienes acceso al panel de vigilantes.')
        return redirect('login')
    
    tenants = Tenant.objects.filter(is_active=True).select_related('assigned_user')
    
    # Búsqueda
    search = request.GET.get('search')
    if search:
        tenants = tenants.filter(
            Q(unit_number__icontains=search) |
            Q(assigned_user__first_name__icontains=search) |
            Q(assigned_user__last_name__icontains=search)
        )
    
    context = {
        'guard': guard,
        'tenants': tenants,
    }
    return render(request, 'guard_panel/tenants.html', context)


@login_required
def guard_reports_view(request):
    """Vista para ver reportes del vigilante"""
    try:
        guard = Guard.objects.get(user=request.user)
    except Guard.DoesNotExist:
        messages.error(request, 'No tienes acceso al panel de vigilantes.')
        return redirect('login')
    
    # Estadísticas del vigilante
    today = timezone.now().date()
    this_month = timezone.now().replace(day=1).date()
    
    context = {
        'guard': guard,
        'visits_approved_today': Visit.objects.filter(
            approved_by=request.user,
            approved_at__date=today
        ).count(),
        'visits_approved_month': Visit.objects.filter(
            approved_by=request.user,
            approved_at__date__gte=this_month
        ).count(),
        'entries_registered_today': Visit.objects.filter(
            entry_guard=guard,
            entry_time__date=today
        ).count(),
        'exits_registered_today': Visit.objects.filter(
            exit_guard=guard,
            exit_time__date=today
        ).count(),
    }
    
    return render(request, 'guard_panel/reports.html', context)
