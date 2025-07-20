from django.urls import path
from . import views

app_name = 'tenants'

urlpatterns = [
    path('', views.tenant_list, name='tenant_list'),
    path('create/', views.tenant_create, name='tenant_create'),
    path('<int:tenant_id>/', views.tenant_detail, name='tenant_detail'),
    path('<int:tenant_id>/edit/', views.tenant_edit, name='tenant_edit'),
    path('<int:tenant_id>/delete/', views.tenant_delete, name='tenant_delete'),
]
