from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Gestión de usuarios
    path('users/', views.users_list, name='users_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('assign-roles/', views.assign_roles, name='assign_roles'),
    path('assign-roles/<int:user_id>/', views.assign_user_role, name='assign_user_role'),
]
