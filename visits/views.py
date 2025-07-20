from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Visit, VisitLog
from .forms import VisitForm
from guards.models import Guard


@login_required
def visit_create(request):
    """Vista para crear una nueva visita"""
    if request.method == 'POST':
        form = VisitForm(request.POST, request.FILES)
        if form.is_valid():
            visit = form.save(commit=False)
            
            # Asignar el guard que registra si existe
            try:
                guard = Guard.objects.get(user=request.user)
                visit.registered_by = guard
            except Guard.DoesNotExist:
                pass
            
            # Manejar la foto de identificación
            if 'id_photo' in request.FILES:
                visit.visitor_photo = request.FILES['id_photo']
            
            visit.save()
            
            # Crear log de creación
            VisitLog.objects.create(
                visit=visit,
                action='created',
                performed_by=getattr(visit, 'registered_by', None),
                notes=f'Visita creada por {request.user.get_full_name()}'
            )
            
            messages.success(request, f'Visita para {visit.visitor_name} registrada exitosamente')
            return redirect('dashboard:visit_detail', visit_id=visit.id)
    else:
        form = VisitForm()
    
    context = {
        'form': form,
        'title': 'Registrar Nueva Visita',
        'button_text': 'Registrar Visita'
    }
    
    # Detectar si es móvil
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    is_mobile = any(device in user_agent.lower() for device in ['mobile', 'android', 'iphone', 'ipad'])
    
    # Usar template simplificado por defecto, o el complejo si se especifica
    if request.GET.get('full') == '1':
        return render(request, 'visits/visit_form.html', context)
    else:
        return render(request, 'visits/visit_form_simple.html', context)


@login_required
def visit_edit(request, visit_id):
    """Vista para editar una visita"""
    visit = get_object_or_404(Visit, id=visit_id)
    
    if request.method == 'POST':
        form = VisitForm(request.POST, instance=visit)
        if form.is_valid():
            visit = form.save()
            
            # Crear log de modificación
            try:
                guard = Guard.objects.get(user=request.user)
            except Guard.DoesNotExist:
                guard = None
                
            VisitLog.objects.create(
                visit=visit,
                action='modified',
                performed_by=guard,
                notes=f'Visita modificada por {request.user.get_full_name()}'
            )
            
            messages.success(request, f'Visita de {visit.visitor_name} actualizada exitosamente')
            return redirect('dashboard:visit_detail', visit_id=visit.id)
    else:
        form = VisitForm(instance=visit)
    
    context = {
        'form': form,
        'visit': visit,
        'title': f'Editar Visita: {visit.visitor_name}',
        'button_text': 'Actualizar Visita'
    }
    
    return render(request, 'visits/visit_form.html', context)


@login_required
def visit_cancel(request, visit_id):
    """Vista para cancelar una visita"""
    visit = get_object_or_404(Visit, id=visit_id)
    
    if request.method == 'POST':
        visit.status = 'cancelada'
        visit.save()
        
        # Crear log de cancelación
        try:
            guard = Guard.objects.get(user=request.user)
        except Guard.DoesNotExist:
            guard = None
            
        VisitLog.objects.create(
            visit=visit,
            action='cancelled',
            performed_by=guard,
            notes=f'Visita cancelada por {request.user.get_full_name()}'
        )
        
        messages.success(request, f'Visita de {visit.visitor_name} cancelada exitosamente')
        return redirect('dashboard:visit_detail', visit_id=visit.id)
    
    return render(request, 'visits/visit_cancel.html', {'visit': visit})
