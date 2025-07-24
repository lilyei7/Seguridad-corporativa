from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    # Dashboard
    path('', views.maintenance_dashboard, name='dashboard'),
    
    # Reportes de Mantenimiento (para inquilinos)
    path('reports/', views.reports_list, name='reports_list'),
    path('reports/create/', views.report_create, name='report_create'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_id>/edit/', views.report_edit, name='report_edit'),
    path('reports/<int:report_id>/delete/', views.report_delete, name='report_delete'),
    
    # Checklists (para administradores)
    path('checklists/', views.checklists_list, name='checklists_list'),
    path('checklists/create/', views.checklist_create, name='checklist_create'),
    path('checklists/<int:checklist_id>/', views.checklist_detail, name='checklist_detail'),
    path('checklists/<int:checklist_id>/update/', views.checklist_update, name='checklist_update'),
    path('checklists/<int:checklist_id>/delete/', views.checklist_delete, name='checklist_delete'),
    
    # Items
    path('items/<int:item_id>/update-status/', views.item_update_status, name='item_update_status'),
    path('items/<int:item_id>/upload-evidence/', views.upload_evidence, name='upload_evidence'),
    
    # Áreas
    path('areas/', views.areas_list, name='areas_list'),
    path('areas/create/', views.area_create, name='area_create'),
    
    # Cámaras
    path('cameras/', views.cameras_list, name='cameras_list'),
    path('cameras/create/', views.camera_create, name='camera_create'),
    path('cameras/<int:camera_id>/', views.camera_detail, name='camera_detail'),
]
