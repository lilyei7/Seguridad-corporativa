from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    # Dashboard
    path('', views.maintenance_dashboard, name='dashboard'),
    
    # Checklists
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
