from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    MaintenanceArea, MaintenanceChecklist, MaintenanceItem, 
    MaintenanceEvidence, Camera, MaintenanceReport, MaintenanceReportImage
)
from .forms import (
    MaintenanceChecklistForm, MaintenanceItemForm, MaintenanceEvidenceForm,
    CameraForm, MaintenanceAreaForm, MaintenanceReportForm, 
    MaintenanceReportImageForm, MaintenanceReportResponseForm
)


def can_access_maintenance(user):
    """Verifica si el usuario puede acceder al sistema de mantenimiento"""
    return (user.is_superuser or 
            user.groups.filter(name__in=['Vigilantes', 'Mantenimiento', 'Inquilinos']).exists())


def notify_admins_new_report(report):
    """Envía notificaciones robustas a administradores sobre nuevo reporte"""
    try:
        from accounts.models import Notification
        
        # Crear notificaciones usando el nuevo sistema
        notifications = Notification.send_maintenance_request(
            sender=report.reported_by,
            title=f"{report.title}",
            message=(
                f"Se ha creado un nuevo reporte de mantenimiento:\n\n"
                f"📋 Título: {report.title}\n"
                f"📂 Categoría: {report.get_category_display()}\n"
                f"⭐ Prioridad: {report.get_priority_display()}\n"
                f"📍 Área: {report.area.name}\n"
                f"👤 Reportado por: {report.reported_by.get_full_name() or report.reported_by.username}\n"
                f"📅 Fecha: {report.created_at.strftime('%d/%m/%Y %H:%M')}\n"
                f"📧 Contacto: {report.contact_email}\n\n"
                f"📝 Descripción:\n{report.description[:300]}{'...' if len(report.description) > 300 else ''}\n\n"
                f"💡 Por favor, revisa y asigna este reporte lo antes posible."
            ),
            maintenance_obj=report,
            action_url=f"/maintenance/reports/{report.id}/",
            requires_action=True,
            action_text="Ver Reporte"
        )
        
        print(f"✅ Notificaciones creadas: {len(notifications)}")
        
        # También enviar email si está configurado
        try:
            send_email_notification(report)
        except Exception as email_error:
            print(f"⚠️ Error enviando email: {email_error}")
        
        return notifications
        
    except Exception as e:
        print(f"❌ Error creando notificaciones: {e}")
        return []


def notify_tenant_update(report, message_text, sender=None):
    """Notificar al inquilino sobre actualizaciones en su reporte"""
    try:
        from accounts.models import Notification
        
        if not report.reported_by:
            return None
        
        notification = Notification.send_maintenance_update(
            maintenance_obj=report,
            tenant_user=report.reported_by,
            title=f"Actualización: {report.title}",
            message=message_text,
            sender=sender,
            action_url=f"/maintenance/reports/{report.id}/",
            action_text="Ver Detalles"
        )
        
        print(f"✅ Notificación enviada a inquilino: {report.reported_by.username}")
        return notification
        
    except Exception as e:
        print(f"❌ Error enviando notificación a inquilino: {e}")
        return None


def send_email_notification(report):
    """Enviar notificación por email (opcional)"""
    try:
        admin_emails = User.objects.filter(
            Q(is_superuser=True) | Q(user_role__role='admin')
        ).values_list('email', flat=True).exclude(email='')
        
        if admin_emails and hasattr(settings, 'EMAIL_HOST'):
            subject = f"🔧 Nuevo Reporte de Mantenimiento - {report.title}"
            message = (
                f"Se ha creado un nuevo reporte de mantenimiento:\n\n"
                f"Título: {report.title}\n"
                f"Categoría: {report.get_category_display()}\n"
                f"Prioridad: {report.get_priority_display()}\n"
                f"Área: {report.area.name}\n"
                f"Reportado por: {report.reported_by.get_full_name()}\n"
                f"Email: {report.contact_email}\n"
                f"Fecha: {report.created_at.strftime('%d/%m/%Y %H:%M')}\n\n"
                f"Descripción:\n{report.description}\n\n"
                f"Por favor, accede al sistema para revisar y asignar este reporte."
            )
            
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@security.com'),
                recipient_list=list(admin_emails),
                fail_silently=True
            )
            
    except Exception as e:
        print(f"❌ Error enviando email: {e}")


@login_required
@user_passes_test(can_access_maintenance)
def maintenance_dashboard(request):
    """Dashboard principal del sistema de mantenimiento"""
    # Verificar si el usuario es inquilino
    is_tenant = request.user.groups.filter(name='Inquilinos').exists()
    
    if is_tenant:
        # Dashboard específico para inquilinos usando MaintenanceReport
        # Reportes creados por el inquilino
        my_requests = MaintenanceReport.objects.filter(
            reported_by=request.user
        ).order_by('-created_at')[:10]
        
        # Estadísticas específicas para el inquilino
        tenant_stats = {
            'my_total_requests': MaintenanceReport.objects.filter(reported_by=request.user).count(),
            'my_pending_requests': MaintenanceReport.objects.filter(
                reported_by=request.user, 
                status='pendiente'
            ).count(),
            'my_in_progress_requests': MaintenanceReport.objects.filter(
                reported_by=request.user, 
                status='en_proceso'
            ).count(),
            'my_completed_requests': MaintenanceReport.objects.filter(
                reported_by=request.user, 
                status='completado'
            ).count(),
        }
        
        context = {
            'is_tenant': True,
            'tenant_stats': tenant_stats,
            'my_requests': my_requests,
        }
        
        return render(request, 'maintenance/tenant_dashboard.html', context)
    
    # Dashboard normal para administradores, vigilantes y personal de mantenimiento
    # Estadísticas generales de checklists
    stats = {
        'total_checklists': MaintenanceChecklist.objects.count(),
        'pending_checklists': MaintenanceChecklist.objects.filter(status='pendiente').count(),
        'in_progress_checklists': MaintenanceChecklist.objects.filter(status='en_proceso').count(),
        'completed_checklists': MaintenanceChecklist.objects.filter(status='completado').count(),
        'attention_required': MaintenanceChecklist.objects.filter(status='requiere_atencion').count(),
        'high_priority_checklists': MaintenanceChecklist.objects.filter(
            priority__in=[1, 2], 
            status__in=['pendiente', 'en_proceso', 'requiere_atencion']
        ).count(),
        'total_areas': MaintenanceArea.objects.filter(is_active=True).count(),
        'total_cameras': Camera.objects.count(),
        'active_cameras': Camera.objects.filter(status='activa').count(),
        'offline_cameras': Camera.objects.filter(status='offline').count(),
        'maintenance_cameras': Camera.objects.filter(status='mantenimiento').count(),
    }
    
    # Estadísticas de reportes de mantenimiento
    report_stats = {
        'total_reports': MaintenanceReport.objects.count(),
        'pending_reports': MaintenanceReport.objects.filter(status='pendiente').count(),
        'in_progress_reports': MaintenanceReport.objects.filter(status='en_proceso').count(),
        'completed_reports': MaintenanceReport.objects.filter(status='completado').count(),
        'attention_required_reports': MaintenanceReport.objects.filter(status='requiere_atencion').count(),
        'high_priority_reports': MaintenanceReport.objects.filter(
            priority__in=[1, 2], 
            status__in=['pendiente', 'en_proceso', 'requiere_atencion']
        ).count(),
        'unassigned_reports': MaintenanceReport.objects.filter(
            assigned_to__isnull=True,
            status__in=['pendiente', 'en_proceso']
        ).count(),
    }
    
    # Checklists recientes
    recent_checklists = MaintenanceChecklist.objects.select_related(
        'area', 'created_by', 'assigned_to'
    ).order_by('-created_at')[:5]
    
    # Reportes recientes (últimos 10)
    recent_reports = MaintenanceReport.objects.select_related(
        'area', 'reported_by', 'assigned_to'
    ).order_by('-created_at')[:10]
    
    # Reportes pendientes y sin asignar (IMPORTANTES)
    pending_reports = MaintenanceReport.objects.filter(
        status='pendiente'
    ).select_related('area', 'reported_by').order_by('-priority', '-created_at')[:5]
    
    # Checklists asignados al usuario actual
    my_checklists = MaintenanceChecklist.objects.filter(
        assigned_to=request.user
    ).exclude(status='completado').order_by('-priority', '-created_at')[:5]
    
    # Reportes asignados al usuario actual
    my_reports = MaintenanceReport.objects.filter(
        assigned_to=request.user
    ).exclude(status='completado').order_by('-priority', '-created_at')[:5]
    
    # Checklists de alta prioridad pendientes
    high_priority_checklists = MaintenanceChecklist.objects.filter(
        priority__in=[1, 2],
        status__in=['pendiente', 'en_proceso', 'requiere_atencion']
    ).order_by('-priority', '-created_at')[:5]
    
    # Reportes de alta prioridad
    high_priority_reports = MaintenanceReport.objects.filter(
        priority__in=[1, 2],
        status__in=['pendiente', 'en_proceso', 'requiere_atencion']
    ).order_by('-priority', '-created_at')[:5]
    
    context = {
        'is_tenant': False,
        'stats': stats,
        'report_stats': report_stats,
        'recent_checklists': recent_checklists,
        'recent_reports': recent_reports,
        'pending_reports': pending_reports,
        'my_checklists': my_checklists,
        'my_reports': my_reports,
        'high_priority_checklists': high_priority_checklists,
        'high_priority_reports': high_priority_reports,
    }
    
    return render(request, 'maintenance/dashboard.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def checklists_list(request):
    """Lista de checklists de mantenimiento"""
    # Verificar si el usuario es inquilino
    is_tenant = request.user.groups.filter(name='Inquilinos').exists()
    
    if is_tenant:
        # Los inquilinos solo ven sus propios checklists
        checklists = MaintenanceChecklist.objects.filter(
            created_by=request.user
        ).select_related('area', 'created_by', 'assigned_to').order_by('-created_at')
    else:
        # Administradores, vigilantes y personal de mantenimiento ven todos
        checklists = MaintenanceChecklist.objects.select_related(
            'area', 'created_by', 'assigned_to'
        ).order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    area_filter = request.GET.get('area', '')
    assigned_filter = request.GET.get('assigned', '')
    search = request.GET.get('search', '')
    
    if status_filter:
        checklists = checklists.filter(status=status_filter)
    
    if priority_filter:
        checklists = checklists.filter(priority=priority_filter)
    
    if area_filter:
        checklists = checklists.filter(area_id=area_filter)
    
    if assigned_filter and not is_tenant:  # Los inquilinos no pueden filtrar por asignado
        checklists = checklists.filter(assigned_to_id=assigned_filter)
    
    if search:
        checklists = checklists.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(area__name__icontains=search)
        )
    
    # Paginación
    paginator = Paginator(checklists, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Opciones para filtros
    areas = MaintenanceArea.objects.filter(is_active=True).order_by('name')
    users = User.objects.filter(
        Q(is_superuser=True) | 
        Q(groups__name__in=['Vigilantes', 'Mantenimiento'])
    ).distinct().order_by('first_name', 'last_name')
    
    context = {
        'is_tenant': is_tenant,
        'page_obj': page_obj,
        'areas': areas,
        'users': users,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'area_filter': area_filter,
        'assigned_filter': assigned_filter,
        'search': search,
    }
    
    return render(request, 'maintenance/checklist_list.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def checklist_create(request):
    """Crear un nuevo checklist de mantenimiento"""
    if request.method == 'POST':
        form = MaintenanceChecklistForm(request.POST)
        if form.is_valid():
            checklist = form.save(commit=False)
            checklist.created_by = request.user
            checklist.save()
            
            # Crear items del checklist si se proporcionaron
            items_data = request.POST.getlist('items[]')
            for i, item_name in enumerate(items_data):
                if item_name.strip():
                    MaintenanceItem.objects.create(
                        checklist=checklist,
                        item_name=item_name.strip(),
                        order=i + 1
                    )
            
            messages.success(request, f'Checklist "{checklist.title}" creado exitosamente.')
            return redirect('maintenance:checklist_detail', checklist.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = MaintenanceChecklistForm()
    
    areas = MaintenanceArea.objects.filter(is_active=True).order_by('name')
    users = User.objects.filter(
        Q(is_superuser=True) | 
        Q(groups__name__in=['Vigilantes', 'Mantenimiento'])
    ).distinct().order_by('first_name', 'last_name')
    
    context = {
        'form': form,
        'areas': areas,
        'users': users,
    }
    
    return render(request, 'maintenance/checklist_create.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def checklist_detail(request, checklist_id):
    """Detalle de un checklist de mantenimiento"""
    checklist = get_object_or_404(
        MaintenanceChecklist.objects.select_related('area', 'created_by', 'assigned_to'),
        id=checklist_id
    )
    
    items = checklist.items.all().order_by('order', 'item_name')
    
    # Calcular progreso
    total_items = items.count()
    completed_items = items.exclude(status='pendiente').count()
    progress_percentage = (completed_items / total_items * 100) if total_items > 0 else 0
    
    context = {
        'checklist': checklist,
        'items': items,
        'total_items': total_items,
        'completed_items': completed_items,
        'progress_percentage': progress_percentage,
    }
    
    return render(request, 'maintenance/checklist_detail.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def item_update_status(request, item_id):
    """Actualizar el estado de un item del checklist"""
    if request.method == 'POST':
        item = get_object_or_404(MaintenanceItem, id=item_id)
        
        status = request.POST.get('status')
        observations = request.POST.get('observations', '')
        
        if status in [choice[0] for choice in MaintenanceItem.ITEM_STATUS_CHOICES]:
            item.status = status
            item.observations = observations
            item.checked_by = request.user
            item.checked_at = timezone.now()
            item.save()
            
            # Si todos los items están completados, marcar el checklist como completado
            pending_items = item.checklist.items.filter(status='pendiente').count()
            if pending_items == 0 and item.checklist.status != 'completado':
                item.checklist.status = 'completado'
                item.checklist.completed_at = timezone.now()
                item.checklist.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Estado actualizado exitosamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Estado no válido'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@user_passes_test(can_access_maintenance)
def upload_evidence(request, item_id):
    """Subir evidencia fotográfica para un item"""
    item = get_object_or_404(MaintenanceItem, id=item_id)
    
    if request.method == 'POST':
        form = MaintenanceEvidenceForm(request.POST, request.FILES)
        if form.is_valid():
            evidence = form.save(commit=False)
            evidence.item = item
            evidence.uploaded_by = request.user
            evidence.save()
            
            messages.success(request, 'Evidencia subida exitosamente.')
            return redirect('maintenance:checklist_detail', item.checklist.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = MaintenanceEvidenceForm()
    
    context = {
        'form': form,
        'item': item,
    }
    
    return render(request, 'maintenance/upload_evidence.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def cameras_list(request):
    """Lista de cámaras del sistema"""
    cameras = Camera.objects.all().order_by('location', 'name')
    
    # Filtros
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    floor_filter = request.GET.get('floor', '')
    search = request.GET.get('search', '')
    
    if status_filter:
        cameras = cameras.filter(status=status_filter)
    
    if type_filter:
        cameras = cameras.filter(camera_type=type_filter)
    
    if floor_filter:
        cameras = cameras.filter(floor=floor_filter)
    
    if search:
        cameras = cameras.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(location__icontains=search)
        )
    
    # Estadísticas
    stats = {
        'total': cameras.count(),
        'active': Camera.objects.filter(status='activa').count(),
        'inactive': Camera.objects.filter(status='inactiva').count(),
        'maintenance': Camera.objects.filter(status='mantenimiento').count(),
        'offline': Camera.objects.filter(status='offline').count(),
    }
    
    # Paginación
    paginator = Paginator(cameras, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Opciones para filtros
    floors = Camera.objects.values_list('floor', flat=True).distinct().order_by('floor')
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'floors': floors,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'floor_filter': floor_filter,
        'search': search,
    }
    
    return render(request, 'maintenance/cameras_list.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def camera_detail(request, camera_id):
    """Detalle de una cámara"""
    camera = get_object_or_404(Camera, id=camera_id)
    
    context = {
        'camera': camera,
    }
    
    return render(request, 'maintenance/camera_detail.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def camera_create(request):
    """Crear una nueva cámara"""
    if request.method == 'POST':
        form = CameraForm(request.POST)
        if form.is_valid():
            camera = form.save()
            messages.success(request, f'Cámara "{camera.name}" creada exitosamente.')
            return redirect('maintenance:camera_detail', camera.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CameraForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'maintenance/camera_create.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def areas_list(request):
    """Lista de áreas de mantenimiento"""
    areas = MaintenanceArea.objects.filter(is_active=True).order_by('name')
    
    # Filtros
    type_filter = request.GET.get('type', '')
    floor_filter = request.GET.get('floor', '')
    search = request.GET.get('search', '')
    
    if type_filter:
        areas = areas.filter(area_type=type_filter)
    
    if floor_filter:
        areas = areas.filter(floor=floor_filter)
    
    if search:
        areas = areas.filter(
            Q(name__icontains=search) |
            Q(location__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Paginación
    paginator = Paginator(areas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Opciones para filtros
    floors = MaintenanceArea.objects.values_list('floor', flat=True).distinct().order_by('floor')
    
    context = {
        'page_obj': page_obj,
        'floors': floors,
        'type_filter': type_filter,
        'floor_filter': floor_filter,
        'search': search,
    }
    
    return render(request, 'maintenance/areas_list.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def area_create(request):
    """Crear una nueva área de mantenimiento"""
    if request.method == 'POST':
        form = MaintenanceAreaForm(request.POST)
        if form.is_valid():
            area = form.save()
            messages.success(request, f'Área "{area.name}" creada exitosamente.')
            return redirect('maintenance:areas_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = MaintenanceAreaForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'maintenance/area_create.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def checklist_update(request, checklist_id):
    """Actualizar un checklist existente"""
    checklist = get_object_or_404(MaintenanceChecklist, id=checklist_id)
    
    # Verificar permisos
    if not (request.user.is_staff or checklist.assigned_to == request.user):
        messages.error(request, 'No tienes permisos para editar este checklist.')
        return redirect('maintenance:checklist_detail', checklist_id)
    
    if request.method == 'POST':
        form = MaintenanceChecklistForm(request.POST, instance=checklist)
        if form.is_valid():
            checklist = form.save()
            messages.success(request, f'Checklist "{checklist.title}" actualizado exitosamente.')
            return redirect('maintenance:checklist_detail', checklist.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = MaintenanceChecklistForm(instance=checklist)
    
    areas = MaintenanceArea.objects.filter(is_active=True).order_by('name')
    users = User.objects.filter(
        Q(is_superuser=True) | 
        Q(groups__name__in=['Vigilantes', 'Mantenimiento'])
    ).distinct().order_by('first_name', 'last_name')
    
    context = {
        'form': form,
        'checklist': checklist,
        'areas': areas,
        'users': users,
        'is_update': True,
    }
    
    return render(request, 'maintenance/checklist_form.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def checklist_delete(request, checklist_id):
    """Eliminar un checklist"""
    checklist = get_object_or_404(MaintenanceChecklist, id=checklist_id)
    
    # Solo staff puede eliminar
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para eliminar checklists.')
        return redirect('maintenance:checklist_detail', checklist_id)
    
    if request.method == 'POST':
        checklist_title = checklist.title
        checklist.delete()
        messages.success(request, f'Checklist "{checklist_title}" eliminado exitosamente.')
        return redirect('maintenance:checklists_list')
    
    context = {
        'checklist': checklist,
    }
    
    return render(request, 'maintenance/checklist_confirm_delete.html', context)


# ==============================================
# REPORTES DE MANTENIMIENTO (Para Inquilinos)
# ==============================================

@login_required
@user_passes_test(can_access_maintenance)
def report_create(request):
    """Vista para crear un nuevo reporte de mantenimiento (para inquilinos)"""
    if request.method == 'POST':
        form = MaintenanceReportForm(request.POST, user=request.user)
        if form.is_valid():
            report = form.save(commit=False)
            report.reported_by = request.user
            
            # Si el usuario provee email de contacto, usarlo, sino usar el del usuario
            if not report.contact_email and request.user.email:
                report.contact_email = request.user.email
            
            report.save()
            
            # Enviar notificaciones robustas a administradores
            is_tenant = request.user.groups.filter(name='Inquilinos').exists()
            notifications_sent = False
            
            try:
                notifications_sent = notify_admins_new_report(report)
                if notifications_sent:
                    print(f"✅ Notificaciones enviadas exitosamente para el reporte: {report.title}")
                else:
                    print(f"⚠️ No se pudieron enviar todas las notificaciones para: {report.title}")
            except Exception as e:
                print(f"❌ Error enviando notificaciones: {e}")
            
            # Mensaje de éxito personalizado
            if is_tenant:
                if notifications_sent:
                    success_message = (
                        f'✅ Reporte de mantenimiento "{report.title}" creado exitosamente. '
                        f'Los administradores han sido notificados y se pondrán en contacto contigo pronto. '
                        f'📧 Recibirás actualizaciones en: {report.contact_email}'
                    )
                else:
                    success_message = (
                        f'⚠️ Reporte de mantenimiento "{report.title}" creado exitosamente, '
                        f'pero hubo problemas enviando algunas notificaciones. '
                        f'El equipo de mantenimiento revisará tu solicitud pronto.'
                    )
            else:
                success_message = f'✅ Reporte de mantenimiento "{report.title}" creado exitosamente.'
            
            messages.success(request, success_message)
            
            # Redirigir según el tipo de usuario
            if is_tenant:
                return redirect('maintenance:report_detail', report_id=report.id)
            else:
                return redirect('maintenance:reports_list')
        else:
            # Si hay errores en el formulario
            messages.error(request, 
                         '❌ Por favor revisa los errores en el formulario y corrige los campos marcados.')
    else:
        form = MaintenanceReportForm(user=request.user)
    
    context = {
        'form': form,
        'page_title': 'Crear Reporte de Mantenimiento',
    }
    
    return render(request, 'maintenance/report_create.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def reports_list(request):
    """Vista para listar reportes de mantenimiento"""
    # Los superusuarios y usuarios con rol admin siempre ven todos los reportes
    is_admin = (request.user.is_superuser or 
                (hasattr(request.user, 'user_role') and 
                 request.user.user_role and 
                 request.user.user_role.role == 'admin'))
    
    # Solo los inquilinos regulares (no admins) ven únicamente sus reportes
    is_tenant_only = (request.user.groups.filter(name='Inquilinos').exists() and 
                      not is_admin)
    
    # Los inquilinos solo ven sus propios reportes
    if is_tenant_only:
        reports = MaintenanceReport.objects.filter(
            reported_by=request.user
        ).select_related('area', 'assigned_to').prefetch_related('images')
    else:
        # Administradores y personal ven todos los reportes
        reports = MaintenanceReport.objects.all().select_related(
            'area', 'reported_by', 'assigned_to'
        ).prefetch_related('images')
    
    # Filtros
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    category_filter = request.GET.get('category')
    area_filter = request.GET.get('area')
    search_query = request.GET.get('search')
    
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    if priority_filter:
        reports = reports.filter(priority=priority_filter)
        
    if category_filter:
        reports = reports.filter(category=category_filter)
        
    if area_filter:
        reports = reports.filter(area_id=area_filter)
    
    if search_query:
        reports = reports.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(specific_location__icontains=search_query)
        )
    
    # Ordenar por fecha de creación (más recientes primero)
    reports = reports.order_by('-created_at')
    
    # Paginación
    paginator = Paginator(reports, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Opciones para filtros
    areas = MaintenanceArea.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_obj': page_obj,
        'reports': page_obj.object_list,
        'areas': areas,
        'status_choices': MaintenanceReport.STATUS_CHOICES,
        'priority_choices': MaintenanceReport.PRIORITY_CHOICES,
        'category_choices': MaintenanceReport.CATEGORY_CHOICES,
        'current_filters': {
            'status': status_filter,
            'priority': priority_filter,
            'category': category_filter,
            'area': area_filter,
            'search': search_query,
        },
        'is_tenant': is_tenant_only,
        'page_title': 'Mis Reportes' if is_tenant_only else 'Reportes de Mantenimiento',
    }
    
    return render(request, 'maintenance/reports_list.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def report_detail(request, report_id):
    """Vista de detalle de un reporte de mantenimiento"""
    report = get_object_or_404(MaintenanceReport, id=report_id)
    
    # Los superusuarios y usuarios con rol admin siempre pueden ver todos los reportes
    is_admin = (request.user.is_superuser or 
                (hasattr(request.user, 'user_role') and 
                 request.user.user_role and 
                 request.user.user_role.role == 'admin'))
    
    # Solo los inquilinos regulares (no admins) ven únicamente sus reportes
    is_tenant_only = (request.user.groups.filter(name='Inquilinos').exists() and 
                      not is_admin)
    
    # Los inquilinos solo pueden ver sus propios reportes
    if is_tenant_only and report.reported_by != request.user:
        messages.error(request, 'No tienes permiso para ver este reporte.')
        return redirect('maintenance:reports_list')
    
    # Formulario para responder (solo para administradores)
    response_form = None
    if not is_tenant_only and request.method == 'POST' and 'update_status' in request.POST:
        response_form = MaintenanceReportResponseForm(request.POST, instance=report)
        if response_form.is_valid():
            old_status = report.status
            updated_report = response_form.save(commit=False)
            
            # Si se marca como completado, establecer fecha de resolución
            if updated_report.status == 'completado' and not updated_report.resolved_at:
                updated_report.resolved_at = timezone.now()
            
            updated_report.save()
            
            # Enviar notificación al inquilino sobre la actualización
            if old_status != updated_report.status or updated_report.response_to_tenant:
                try:
                    # Determinar tipo de notificación basado en el estado
                    if updated_report.status == 'completado':
                        notification_type = 'maintenance_completed'
                        title_prefix = "✅ Completado"
                        priority = 3
                    elif updated_report.status == 'en_proceso':
                        notification_type = 'maintenance_update'
                        title_prefix = "🔄 En Proceso"
                        priority = 3
                    elif updated_report.status == 'rechazado':
                        notification_type = 'maintenance_rejected'
                        title_prefix = "❌ Rechazado"
                        priority = 2
                    else:
                        notification_type = 'maintenance_update'
                        title_prefix = "📋 Actualización"
                        priority = 3
                    
                    # Mensaje de notificación
                    message_parts = [
                        f"Tu reporte de mantenimiento ha sido actualizado:\n",
                        f"📋 Título: {updated_report.title}",
                        f"📊 Estado: {updated_report.get_status_display()}",
                        f"👤 Actualizado por: {request.user.get_full_name() or request.user.username}",
                        f"📅 Fecha: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
                    ]
                    
                    if updated_report.assigned_to:
                        message_parts.append(f"🔧 Asignado a: {updated_report.assigned_to.get_full_name()}")
                    
                    if updated_report.response_to_tenant:
                        message_parts.append(f"\n💬 Respuesta del administrador:\n{updated_report.response_to_tenant}")
                    
                    if updated_report.status == 'completado':
                        message_parts.append("\n🎉 ¡Tu solicitud ha sido completada exitosamente!")
                    elif updated_report.status == 'rechazado':
                        message_parts.append("\n⚠️ Tu solicitud ha sido rechazada. Consulta la respuesta del administrador para más detalles.")
                    
                    message = "\n".join(message_parts)
                    
                    # Enviar notificación
                    notify_tenant_update(
                        report=updated_report,
                        message_text=message,
                        sender=request.user
                    )
                    
                except Exception as e:
                    print(f"⚠️ Error enviando notificación al inquilino: {e}")
            
            messages.success(request, 'Reporte actualizado exitosamente.')
            return redirect('maintenance:report_detail', report_id=report.id)
    elif not is_tenant_only:
        response_form = MaintenanceReportResponseForm(instance=report)
    
    # Formulario para subir imágenes
    image_form = None
    if request.method == 'POST' and 'upload_image' in request.POST:
        image_form = MaintenanceReportImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            image = image_form.save(commit=False)
            image.report = report
            image.uploaded_by = request.user
            image.save()
            messages.success(request, 'Imagen subida exitosamente.')
            return redirect('maintenance:report_detail', report_id=report.id)
    else:
        image_form = MaintenanceReportImageForm()
    
    context = {
        'report': report,
        'response_form': response_form,
        'image_form': image_form,
        'is_tenant': is_tenant_only,
        'can_edit': not is_tenant_only,
        'page_title': f'Reporte: {report.title}',
    }
    
    return render(request, 'maintenance/report_detail.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def report_edit(request, report_id):
    """Vista para editar un reporte de mantenimiento"""
    report = get_object_or_404(MaintenanceReport, id=report_id)
    
    # Los inquilinos solo pueden editar sus propios reportes y solo si están pendientes
    is_tenant = request.user.groups.filter(name='Inquilinos').exists()
    if is_tenant:
        if report.reported_by != request.user:
            messages.error(request, 'No tienes permiso para editar este reporte.')
            return redirect('maintenance:reports_list')
        if report.status != 'pendiente':
            messages.error(request, 'Solo puedes editar reportes que están pendientes.')
            return redirect('maintenance:report_detail', report_id=report.id)
    
    if request.method == 'POST':
        form = MaintenanceReportForm(request.POST, instance=report, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reporte actualizado exitosamente.')
            return redirect('maintenance:report_detail', report_id=report.id)
    else:
        form = MaintenanceReportForm(instance=report, user=request.user)
    
    context = {
        'form': form,
        'report': report,
        'is_editing': True,
        'is_tenant': is_tenant,
        'page_title': f'Editar Reporte: {report.title}',
    }
    
    return render(request, 'maintenance/report_create.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def report_delete(request, report_id):
    """Vista para eliminar un reporte de mantenimiento"""
    report = get_object_or_404(MaintenanceReport, id=report_id)
    
    # Los inquilinos solo pueden eliminar sus propios reportes y solo si están pendientes
    is_tenant = request.user.groups.filter(name='Inquilinos').exists()
    if is_tenant:
        if report.reported_by != request.user:
            messages.error(request, 'No tienes permiso para eliminar este reporte.')
            return redirect('maintenance:reports_list')
        if report.status != 'pendiente':
            messages.error(request, 'Solo puedes eliminar reportes que están pendientes.')
            return redirect('maintenance:report_detail', report_id=report.id)
    
    if request.method == 'POST':
        report_title = report.title
        report.delete()
        messages.success(request, f'Reporte "{report_title}" eliminado exitosamente.')
        return redirect('maintenance:reports_list')
    
    context = {
        'report': report,
        'is_tenant': is_tenant,
        'page_title': f'Eliminar Reporte: {report.title}',
    }
    
    return render(request, 'maintenance/report_confirm_delete.html', context)
