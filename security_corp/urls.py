"""
URL configuration for security_corp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from dashboard.views import login_view, logout_view
from dashboard.icon_views import favicon_view, apple_touch_icon_view, serve_xd_icon_direct
from test_notifications_view import test_notifications

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='home'),
    path('login/', login_view, name='login'),  # Añadir esta línea específica para login
    path('logout/', logout_view, name='logout'),
    path('test-notifications/', test_notifications, name='test_notifications'),
    
    # Iconos para PWA - Solucionar errores 404
    path('favicon.ico', favicon_view, name='favicon'),
    path('apple-touch-icon.png', serve_xd_icon_direct, name='apple_touch_icon'),
    path('apple-touch-icon-precomposed.png', serve_xd_icon_direct, name='apple_touch_icon_precomposed'),
    path('apple-touch-icon-120x120.png', serve_xd_icon_direct, name='apple_touch_icon_120'),
    path('apple-touch-icon-120x120-precomposed.png', serve_xd_icon_direct, name='apple_touch_icon_120_precomposed'),
    
    # PWA Demo
    path('pwa-demo/', TemplateView.as_view(template_name='pwa_demo.html'), name='pwa_demo'),
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),
    
    # Dashboard principal (original)
    path('dashboard/', include('dashboard.urls')),
    
    # Paneles específicos por rol - URLs en español
    path('administracion/', include('admin_panel.urls')),
    path('inquilino/', include('tenant_panel.urls')),
    path('vigilante/', include('guard_panel.urls')),
    
    # Versiones móviles optimizadas
    path('', include('mobile_app.urls')),
    
    # Push notifications
    path('notifications/', include('notifications.urls')),
    
    # Apps originales (mantener compatibilidad)
    path('tenants/', include('tenants.urls')),
    path('visits/', include('visits.urls')),
    path('guards/', include('guards.urls')),
    path('accounts/', include('accounts.urls')),
    path('maintenance/', include('maintenance.urls')),
    
    # APIs
    path('api/', include('accounts.api_urls')),
    path('api/maintenance/', include('maintenance.api_urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
