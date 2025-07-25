from django.http import HttpResponse, Http404, FileResponse
from django.conf import settings
from django.shortcuts import redirect
import os

def serve_xd_icon_direct(request):
    """Serve xd.png icon directly without redirect"""
    try:
        # Construir la ruta al archivo xd.png
        icon_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'icons', 'xd.png')
        
        # Si no existe en STATIC_ROOT, intentar con STATICFILES_DIRS
        if not os.path.exists(icon_path) and hasattr(settings, 'STATICFILES_DIRS'):
            icon_path = os.path.join(settings.STATICFILES_DIRS[0], 'icons', 'xd.png')
        
        if os.path.exists(icon_path):
            return FileResponse(
                open(icon_path, 'rb'),
                content_type='image/png',
                headers={
                    'Cache-Control': 'public, max-age=86400',  # Cache por 24 horas
                    'Content-Disposition': 'inline; filename="apple-touch-icon.png"'
                }
            )
        else:
            # Fallback a redirect si no encontramos el archivo
            return redirect('/static/icons/xd.png')
    except Exception as e:
        return redirect('/static/icons/xd.png')

def favicon_view(request):
    """Serve favicon from static files"""
    try:
        # Redirect to your custom icon
        return redirect('/static/icons/xd.png')
    except:
        raise Http404("Favicon not found")

def apple_touch_icon_view(request):
    """Serve Apple touch icon from static files"""
    try:
        return redirect('/static/icons/xd.png')
    except:
        raise Http404("Apple touch icon not found")
