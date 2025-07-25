from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth.models import Group

from tenants.models import Tenant
from guards.models import Guard, Shift
from visits.models import Visit, VisitLog
from .models import SecurityIncident, SecurityCheckpoint, SystemThemeConfiguration, UserThemePreference
from .forms import SecurityIncidentForm, IncidentStatusForm


def get_user_role_redirect(user):
    """
    Determina a qué panel debe ser redirigido el usuario según su rol
    """
    # 1. Administradores y staff
    if user.is_staff or user.is_superuser:
        return '/administracion/'
    
    # 2. Vigilantes
    try:
        guard = Guard.objects.get(user=user)
        if guard.status == 'activo':
            return '/vigilante/'
    except Guard.DoesNotExist:
        pass
    
    # 3. Inquilinos
    try:
        tenant = Tenant.objects.get(assigned_user=user)
        if tenant.is_active:
            return '/inquilino/'
    except Tenant.DoesNotExist:
        pass
    
    # 4. Default: dashboard original
    return 'dashboard:index'


def login_view(request):
    """Vista para el login del sistema"""
    if request.user.is_authenticated:
        # Redirigir según el rol del usuario
        redirect_url = get_user_role_redirect(request.user)
        return redirect(redirect_url)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Determinar redirección según rol
            redirect_url = get_user_role_redirect(user)
            next_url = request.GET.get('next', redirect_url)
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'login.html')


def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    return redirect('login')


@login_required
def dashboard_index(request):
    """Vista principal del dashboard que redirige según el tipo de usuario"""
    
    # Redirección automática según el rol del usuario
    redirect_url = get_user_role_redirect(request.user)
    
    # Si la redirección no es al dashboard original, redirigir
    if redirect_url != 'dashboard:index':
        return redirect(redirect_url)
    
    # Solo continuar aquí si no hay un panel específico para el usuario
    # (usuarios sin rol específico verán el dashboard original)
    
    # Detectar si es dispositivo móvil
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone', 'ipad', 'tablet'])
    
    # Si es móvil, usar el dashboard móvil unificado
    if is_mobile:
        # Preparar contexto común para vista móvil
        context = {
            'user': request.user,
            'is_mobile': True,
        }
        
        # Agregar datos específicos según el rol
        if request.user.is_superuser or request.user.groups.filter(name__in=['Administradores', 'Supervisores']).exists():
            context.update({
                'user_role': 'admin',
                'total_visits_today': Visit.objects.filter(created_at__date=timezone.now().date()).count(),
                'active_guards': Guard.objects.filter(status='activo').count(),
                'pending_incidents': SecurityIncident.objects.filter(status='open').count(),
            })
        elif request.user.groups.filter(name='Vigilantes').exists():
            context.update({
                'user_role': 'guard',
                'my_shift_today': Shift.objects.filter(
                    guard__user=request.user,
                    date=timezone.now().date()
                ).first(),
                'visits_today': Visit.objects.filter(created_at__date=timezone.now().date()).count(),
            })
        elif request.user.groups.filter(name='Inquilinos').exists():
            context.update({
                'user_role': 'tenant',
                'my_visits': Visit.objects.filter(
                    tenant__assigned_user=request.user
                ).order_by('-created_at')[:5],
            })
        
        return render(request, 'dashboard/mobile_index.html', context)
    
    # Para desktop, usar las redirecciones existentes
    if request.user.is_superuser:
        return redirect('dashboard:admin_panel')
    elif request.user.groups.filter(name='Vigilantes').exists():
        return redirect('dashboard:guard_panel')
    elif request.user.groups.filter(name='Inquilinos').exists():
        return redirect('dashboard:tenant_panel')
    else:
        # Usuario sin grupo específico, redirigir al panel de admin
        return redirect('dashboard:admin_panel')


@login_required
def visits_list(request):
    """Vista para listar todas las visitas"""
    visits = Visit.objects.select_related('tenant', 'registered_by').order_by('-scheduled_date', '-scheduled_time')
    
    # Filtros
    status_filter = request.GET.get('status')
    date_filter = request.GET.get('date')
    tenant_filter = request.GET.get('tenant')
    
    if status_filter:
        visits = visits.filter(status=status_filter)
    
    if date_filter:
        visits = visits.filter(scheduled_date=date_filter)
    
    if tenant_filter:
        visits = visits.filter(tenant_id=tenant_filter)
    
    tenants = Tenant.objects.filter(is_active=True).order_by('tenant_name')
    
    context = {
        'visits': visits,
        'tenants': tenants,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'tenant_filter': tenant_filter,
    }
    
    return render(request, 'dashboard/visits_list.html', context)


@login_required
def tenants_list(request):
    """Vista para listar todos los inquilinos"""
    tenants = Tenant.objects.all().order_by('tenant_name')
    
    # Estadísticas por inquilino
    for tenant in tenants:
        tenant.total_visits = Visit.objects.filter(tenant=tenant).count()
        tenant.pending_visits = Visit.objects.filter(
            tenant=tenant, 
            status='pendiente'
        ).count()
    
    context = {
        'tenants': tenants,
    }
    
    return render(request, 'dashboard/tenants_list.html', context)


@login_required
def guards_list(request):
    """Vista para listar todos los guardias"""
    guards = Guard.objects.select_related('user').order_by('user__first_name', 'user__last_name')
    
    context = {
        'guards': guards,
    }
    
    return render(request, 'dashboard/guards_list.html', context)


@login_required
def visit_detail(request, visit_id):
    """Vista para ver los detalles de una visita"""
    visit = get_object_or_404(Visit, id=visit_id)
    logs = visit.logs.all().order_by('-timestamp')
    
    context = {
        'visit': visit,
        'logs': logs,
    }
    
    return render(request, 'dashboard/visit_detail.html', context)


@login_required
def mark_visit_arrived(request, visit_id):
    """Marcar una visita como llegada"""
    if request.method == 'POST':
        visit = get_object_or_404(Visit, id=visit_id)
        
        # Obtener el guard del usuario actual si existe
        guard = None
        try:
            guard = Guard.objects.get(user=request.user)
        except Guard.DoesNotExist:
            pass
        
        visit.mark_arrived(guard)
        
        # Crear log de la acción
        VisitLog.objects.create(
            visit=visit,
            action='arrived',
            performed_by=guard,
            notes=f'Marcada como llegada por {request.user.get_full_name()}'
        )
        
        messages.success(request, f'Visita de {visit.visitor_name} marcada como llegada')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
    
    return redirect('dashboard:visit_detail', visit_id=visit_id)


@login_required
def mark_visit_departed(request, visit_id):
    """Marcar una visita como completada"""
    if request.method == 'POST':
        visit = get_object_or_404(Visit, id=visit_id)
        
        guard = None
        try:
            guard = Guard.objects.get(user=request.user)
        except Guard.DoesNotExist:
            pass
        
        visit.mark_departed()
        
        # Crear log de la acción
        VisitLog.objects.create(
            visit=visit,
            action='departed',
            performed_by=guard,
            notes=f'Marcada como completada por {request.user.get_full_name()}'
        )
        
        messages.success(request, f'Visita de {visit.visitor_name} marcada como completada')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
    
    return redirect('dashboard:visit_detail', visit_id=visit_id)


# Nuevos paneles para diferentes tipos de usuario

@login_required
def admin_panel(request):
    """Panel completo para administradores"""
    today = timezone.now().date()
    
    # Estadísticas generales
    total_tenants = Tenant.objects.filter(is_active=True).count()
    total_guards = Guard.objects.filter(status='activo').count()
    
    # Visitas de hoy
    today_visits = Visit.objects.filter(scheduled_date=today)
    pending_visits = today_visits.filter(status='pendiente').count()
    completed_visits = today_visits.filter(status='completada').count()
    in_progress_visits = today_visits.filter(status='en_progreso').count()
    
    # Incidentes de seguridad recientes
    recent_incidents = SecurityIncident.objects.filter(
        created_at__gte=today
    ).order_by('-created_at')[:5]
    
    # Visitas próximas
    upcoming_visits = Visit.objects.filter(
        scheduled_date=today,
        status='pendiente',
    ).order_by('scheduled_time')[:5]
    
    # Guardias en turno actual
    current_hour = timezone.now().time()
    guards_on_duty = Shift.objects.filter(
        date=today,
        start_time__lte=current_hour,
        end_time__gte=current_hour
    ).select_related('guard')
    
    context = {
        'total_tenants': total_tenants,
        'total_guards': total_guards,
        'pending_visits': pending_visits,
        'completed_visits': completed_visits,
        'in_progress_visits': in_progress_visits,
        'recent_incidents': recent_incidents,
        'upcoming_visits': upcoming_visits,
        'guards_on_duty': guards_on_duty,
        'today': today,
        'user_type': 'admin',
        # Datos para configuración de sistema
        'theme_choices': SystemThemeConfiguration.THEME_CHOICES,
        'active_config': SystemThemeConfiguration.get_active_config(),
    }
    
    return render(request, 'dashboard/admin_panel.html', context)


@login_required
def guard_panel(request):
    """Panel para vigilantes"""
    # Verificar que el usuario sea vigilante
    if not request.user.groups.filter(name='Vigilantes').exists() and not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard:admin_panel')
    
    today = timezone.now().date()
    
    try:
        guard = Guard.objects.get(user=request.user)
    except Guard.DoesNotExist:
        guard = None
    
    # Visitas pendientes que necesitan aprobación
    pending_visits = Visit.objects.filter(
        status='pendiente'
    ).select_related('tenant')[:10]
    
    # Visitas de hoy
    todays_visits = Visit.objects.filter(
        scheduled_date=today
    ).select_related('tenant').order_by('scheduled_time')
    
    # Estadísticas del día
    total_visits_today = todays_visits.count()
    approved_today = todays_visits.filter(status__in=['aprobada', 'en_progreso', 'completada']).count()
    pending_today = todays_visits.filter(status='pendiente').count()
    
    # Obtener incidentes recientes
    recent_incidents = SecurityIncident.objects.all().order_by('-created_at')[:3]
    
    context = {
        'guard': guard,
        'pending_visits': pending_visits,
        'todays_visits': todays_visits,
        'total_visits_today': total_visits_today,
        'approved_today': approved_today,
        'pending_today': pending_today,
        'recent_visits': pending_visits,  # Para compatibilidad con template móvil
        'recent_incidents': recent_incidents,
        'user_type': 'guard'
    }
    
    # Detectar si es móvil
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    is_mobile = any(device in user_agent.lower() for device in ['mobile', 'android', 'iphone', 'ipad'])
    
    # Usar template móvil si es necesario
    if is_mobile or request.GET.get('mobile') == '1':
        return render(request, 'dashboard/mobile_guard_panel.html', context)
    
    return render(request, 'dashboard/guard_panel.html', context)


@login_required
def tenant_panel(request):
    """Panel para inquilinos - simplificado"""
    # Verificar que el usuario sea inquilino
    if not request.user.groups.filter(name='Inquilinos').exists():
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para acceder al panel de inquilinos.')
            return redirect('dashboard:admin_panel')
    
    try:
        # Buscar inquilino asociado al usuario - lógica simplificada
        tenant = Tenant.objects.filter(assigned_user=request.user).first()
        
        if not tenant:
            # Buscar por email como fallback
            tenant = Tenant.objects.filter(contact_email=request.user.email).first()
            
        if not tenant:
            messages.warning(request, 'No se encontró información de inquilino asociada a tu usuario.')
            # Crear un inquilino demo si no existe
            tenant = Tenant.objects.create(
                tenant_name=f'Inquilino {request.user.username}',
                contact_person=f'{request.user.first_name} {request.user.last_name}' or request.user.username,
                contact_email=request.user.email,
                contact_phone='555-0000',
                address='Dirección por definir',
                city='Ciudad',
                state='Estado',
                zip_code='00000',
                numero_oficina='TBD',
                piso='1',
                assigned_user=request.user,
                is_active=True
            )
            messages.info(request, 'Se ha creado un perfil de inquilino temporal. Contacta al administrador para actualizar la información.')
            
    except Exception as e:
        messages.error(request, f'Error al buscar información del inquilino: {str(e)}')
        return redirect('dashboard:admin_panel')
    
    if tenant:
        # Mis visitas
        my_visits = Visit.objects.filter(
            tenant=tenant
        ).order_by('-created_at')[:10]
        
        # Estadísticas detalladas
        total_visits = Visit.objects.filter(tenant=tenant).count()
        pending_visits = Visit.objects.filter(tenant=tenant, status='pendiente').count()
        approved_visits = Visit.objects.filter(tenant=tenant, status='aprobada').count()
        completed_visits = Visit.objects.filter(tenant=tenant, status='completada').count()
        cancelled_visits = Visit.objects.filter(tenant=tenant, status='cancelada').count()
        
        # Visitas de hoy
        today = timezone.now().date()
        todays_visits = Visit.objects.filter(
            tenant=tenant,
            scheduled_date=today
        ).order_by('scheduled_time')
        
        # Visitas de esta semana
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        this_week_visits = Visit.objects.filter(
            tenant=tenant,
            scheduled_date__range=[week_start, week_end]
        ).count()
        
        # Próximas visitas (próximos 7 días)
        next_week = today + timedelta(days=7)
        upcoming_visits = Visit.objects.filter(
            tenant=tenant,
            scheduled_date__range=[today, next_week],
            status__in=['pendiente', 'aprobada']
        ).order_by('scheduled_date', 'scheduled_time')[:5]
        
    else:
        # Usuario sin inquilino asociado - crear datos por defecto
        my_visits = []
        total_visits = 0
        pending_visits = 0
        approved_visits = 0
        completed_visits = 0
        cancelled_visits = 0
        todays_visits = []
        this_week_visits = 0
        upcoming_visits = []
        
        # Mensaje informativo
        messages.info(request, 
            'No se encontró un local asociado a tu usuario. '
            'Si eres inquilino, contacta al administrador para que configure tu perfil.'
        )
    
    # Información adicional del usuario
    user_info = {
        'username': request.user.username,
        'full_name': request.user.get_full_name() or request.user.username,
        'email': request.user.email,
        'role': 'Inquilino',
        'is_active': request.user.is_active,
        'date_joined': request.user.date_joined,
    }
    
    context = {
        'tenant': tenant,
        'user_info': user_info,
        'my_visits': my_visits,
        'total_visits': total_visits,
        'pending_visits': pending_visits,
        'approved_visits': approved_visits,
        'completed_visits': completed_visits,
        'cancelled_visits': cancelled_visits,
        'todays_visits': todays_visits,
        'this_week_visits': this_week_visits,
        'upcoming_visits': upcoming_visits,
        'user_type': 'tenant',
        'page_title': f'Panel de Inquilino - {user_info["full_name"]}',
    }
    
    # Detectar si es dispositivo móvil
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone', 'ipad', 'tablet'])
    
    # Usar template móvil si es necesario
    if is_mobile or request.GET.get('mobile') == '1':
        return render(request, 'dashboard/mobile_tenant_panel.html', context)
    
    return render(request, 'dashboard/tenant_panel.html', context)


# =============================================================================
# VISTAS PARA INCIDENTES DE SEGURIDAD
# =============================================================================

@login_required
def incidents_list(request):
    """Vista para listar todos los incidentes de seguridad"""
    incidents = SecurityIncident.objects.all().order_by('-incident_datetime')
    
    # Filtros
    status_filter = request.GET.get('status')
    severity_filter = request.GET.get('severity')
    type_filter = request.GET.get('type')
    
    if status_filter:
        incidents = incidents.filter(status=status_filter)
    if severity_filter:
        incidents = incidents.filter(severity=severity_filter)
    if type_filter:
        incidents = incidents.filter(incident_type=type_filter)
    
    context = {
        'incidents': incidents,
        'status_choices': SecurityIncident.STATUS_CHOICES,
        'severity_choices': SecurityIncident.SEVERITY_LEVELS,
        'type_choices': SecurityIncident.INCIDENT_TYPES,
        'current_status': status_filter,
        'current_severity': severity_filter,
        'current_type': type_filter,
    }
    return render(request, 'dashboard/incidents_list.html', context)


@login_required
def incident_create(request):
    """Vista para crear un nuevo incidente de seguridad"""
    if request.method == 'POST':
        form = SecurityIncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = request.user
            incident.save()
            
            messages.success(request, 'Incidente reportado exitosamente.')
            return redirect('dashboard:incident_detail', incident_id=incident.id)
    else:
        form = SecurityIncidentForm()
        # Prellenar la fecha actual
        form.initial['incident_datetime'] = timezone.now().strftime('%Y-%m-%dT%H:%M')
    
    # Detectar si es móvil
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    is_mobile = any(device in user_agent.lower() for device in ['mobile', 'android', 'iphone', 'ipad'])
    
    context = {
        'form': form,
        'title': 'Reportar Incidente de Seguridad'
    }
    
    # Usar template móvil si es necesario
    if is_mobile or request.GET.get('mobile') == '1':
        return render(request, 'dashboard/mobile_incident_form.html', context)
    
    return render(request, 'dashboard/incident_form.html', context)


@login_required
def incident_detail(request, incident_id):
    """Vista para ver los detalles de un incidente"""
    incident = get_object_or_404(SecurityIncident, id=incident_id)
    
    # Formulario para actualizar estado (solo para supervisores/admin)
    status_form = None
    if request.user.is_staff or request.user.groups.filter(name='Supervisores').exists():
        if request.method == 'POST' and 'update_status' in request.POST:
            status_form = IncidentStatusForm(request.POST, instance=incident)
            if status_form.is_valid():
                updated_incident = status_form.save(commit=False)
                if updated_incident.status == 'resuelto' and not incident.resolved_at:
                    updated_incident.resolved_at = timezone.now()
                updated_incident.save()
                messages.success(request, 'Estado del incidente actualizado.')
                return redirect('dashboard:incident_detail', incident_id=incident.id)
        else:
            status_form = IncidentStatusForm(instance=incident)
    
    context = {
        'incident': incident,
        'status_form': status_form,
        'can_edit': request.user.is_staff or request.user.groups.filter(name='Supervisores').exists()
    }
    return render(request, 'dashboard/incident_detail.html', context)


@login_required
def incident_edit(request, incident_id):
    """Vista para editar un incidente existente"""
    incident = get_object_or_404(SecurityIncident, id=incident_id)
    
    # Solo el reportador o supervisores pueden editar
    if not (incident.reported_by == request.user or request.user.is_staff or 
            request.user.groups.filter(name='Supervisores').exists()):
        messages.error(request, 'No tienes permisos para editar este incidente.')
        return redirect('dashboard:incident_detail', incident_id=incident.id)
    
    if request.method == 'POST':
        form = SecurityIncidentForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            messages.success(request, 'Incidente actualizado exitosamente.')
            return redirect('dashboard:incident_detail', incident_id=incident.id)
    else:
        form = SecurityIncidentForm(instance=incident)
    
    context = {
        'form': form,
        'incident': incident,
        'title': 'Editar Incidente'
    }
    return render(request, 'dashboard/incident_form.html', context)


@login_required
def my_shift(request):
    """Vista para mostrar el turno actual del usuario"""
    context = {
        'title': 'Mi Turno',
        'current_time': timezone.now(),
    }
    
    # Si el usuario es un guardia, mostrar información del turno
    if hasattr(request.user, 'guard_profile'):
        guard = request.user.guard_profile
        today = timezone.now().date()
        current_shift = Shift.objects.filter(
            guard=guard,
            date=today
        ).first()
        
        context.update({
            'guard': guard,
            'current_shift': current_shift,
            'is_guard': True
        })
    else:
        context['is_guard'] = False
    
    return render(request, 'dashboard/my_shift.html', context)
