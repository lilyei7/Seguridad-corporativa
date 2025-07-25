from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from tenants.models import Tenant
from guards.models import Guard
from visits.models import Visit
from maintenance.models import MaintenanceReport


class AdminPanelMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin para verificar que el usuario sea administrador"""
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder al panel de administración.')
        return redirect('dashboard:index')


class AdminDashboardView(AdminPanelMixin, TemplateView):
    """Vista principal del panel de administración"""
    template_name = 'admin_panel/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        context.update({
            'total_tenants': Tenant.objects.count(),
            'total_guards': Guard.objects.count(),
            'total_visits_today': Visit.objects.filter(
                created_at__date=timezone.now().date()
            ).count(),
            'pending_maintenance': MaintenanceReport.objects.filter(
                status='pending'
            ).count(),
        })
        
        # Visitas por estado hoy
        today = timezone.now().date()
        context['visits_today'] = {
            'pending': Visit.objects.filter(
                created_at__date=today,
                status='pending'
            ).count(),
            'approved': Visit.objects.filter(
                created_at__date=today,
                status='approved'
            ).count(),
            'completed': Visit.objects.filter(
                created_at__date=today,
                status='completed'
            ).count(),
            'cancelled': Visit.objects.filter(
                created_at__date=today,
                status='cancelled'
            ).count(),
        }
        
        # Visitas recientes
        context['recent_visits'] = Visit.objects.select_related(
            'tenant', 'approved_by'
        ).order_by('-created_at')[:10]
        
        # Reportes de mantenimiento urgentes
        context['urgent_maintenance'] = MaintenanceReport.objects.filter(
            priority__in=['critical', 'high'],
            status='pending'
        ).order_by('priority', '-created_at')[:5]
        
        return context


@login_required
def admin_users_view(request):
    """Vista para gestión de usuarios"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard:index')
    
    from django.contrib.auth.models import User
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'users': users,
        'total_users': users.count(),
        'active_users': users.filter(is_active=True).count(),
        'staff_users': users.filter(is_staff=True).count(),
    }
    
    return render(request, 'admin_panel/users.html', context)


@login_required
def admin_system_view(request):
    """Vista para configuración del sistema"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard:index')
    
    # Estadísticas del sistema
    context = {
        'system_stats': {
            'total_tenants': Tenant.objects.count(),
            'active_tenants': Tenant.objects.filter(is_active=True).count(),
            'total_guards': Guard.objects.count(),
            'active_guards': Guard.objects.filter(is_active=True).count(),
            'total_visits_month': Visit.objects.filter(
                created_at__month=timezone.now().month,
                created_at__year=timezone.now().year
            ).count(),
            'maintenance_reports_month': MaintenanceReport.objects.filter(
                created_at__month=timezone.now().month,
                created_at__year=timezone.now().year
            ).count(),
        }
    }
    
    return render(request, 'admin_panel/system.html', context)


@login_required
def admin_reports_view(request):
    """Vista para reportes y análisis"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard:index')
    
    # Reportes de los últimos 30 días
    last_30_days = timezone.now() - timedelta(days=30)
    
    context = {
        'visits_last_30_days': Visit.objects.filter(
            created_at__gte=last_30_days
        ).values('created_at__date').annotate(
            count=Count('id')
        ).order_by('created_at__date'),
        
        'maintenance_by_priority': MaintenanceReport.objects.filter(
            created_at__gte=last_30_days
        ).values('priority').annotate(
            count=Count('id')
        ),
        
        'most_active_tenants': Tenant.objects.annotate(
            visit_count=Count('visit', filter=Q(visit__created_at__gte=last_30_days))
        ).order_by('-visit_count')[:10],
    }
    
    return render(request, 'admin_panel/reports.html', context)
