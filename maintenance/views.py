from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import (
    MaintenanceArea, MaintenanceChecklist, MaintenanceItem, 
    MaintenanceEvidence, Camera
)
from .forms import (
    MaintenanceChecklistForm, MaintenanceItemForm, MaintenanceEvidenceForm,
    CameraForm, MaintenanceAreaForm
)


def can_access_maintenance(user):
    """Verifica si el usuario puede acceder al sistema de mantenimiento"""
    return (user.is_superuser or 
            user.groups.filter(name__in=['Vigilantes', 'Mantenimiento']).exists())


@login_required
@user_passes_test(can_access_maintenance)
def maintenance_dashboard(request):
    """Dashboard principal del sistema de mantenimiento"""
    # Estadísticas generales
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
    
    # Checklists recientes
    recent_checklists = MaintenanceChecklist.objects.select_related(
        'area', 'created_by', 'assigned_to'
    ).order_by('-created_at')[:10]
    
    # Checklists asignados al usuario actual
    my_checklists = MaintenanceChecklist.objects.filter(
        assigned_to=request.user
    ).exclude(status='completado').order_by('-priority', '-created_at')[:5]
    
    # Checklists de alta prioridad pendientes
    high_priority_checklists = MaintenanceChecklist.objects.filter(
        priority__in=[1, 2],
        status__in=['pendiente', 'en_proceso', 'requiere_atencion']
    ).order_by('-priority', '-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_checklists': recent_checklists,
        'my_checklists': my_checklists,
        'high_priority_checklists': high_priority_checklists,
    }
    
    return render(request, 'maintenance/dashboard.html', context)


@login_required
@user_passes_test(can_access_maintenance)
def checklists_list(request):
    """Lista de checklists de mantenimiento"""
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
    
    if assigned_filter:
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
