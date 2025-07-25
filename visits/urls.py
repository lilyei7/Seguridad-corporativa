from django.urls import path
from . import views

app_name = 'visits'

urlpatterns = [
    # Lista de visitas
    path('', views.visit_list, name='visit_list'),
    
    path('create/', views.visit_create, name='visit_create'),
    path('<int:visit_id>/edit/', views.visit_edit, name='visit_edit'),
    path('<int:visit_id>/cancel/', views.visit_cancel, name='visit_cancel'),
]
