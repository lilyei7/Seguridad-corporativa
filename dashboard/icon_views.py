from django.http import HttpResponse, Http404
from django.conf import settings
import os

def favicon_view(request):
    """Serve favicon from static files"""
    try:
        # Redirect to your custom icon
        from django.shortcuts import redirect
        return redirect('/static/icons/xd.png')
    except:
        raise Http404("Favicon not found")

def apple_touch_icon_view(request):
    """Serve Apple touch icon from static files"""
    try:
        from django.shortcuts import redirect
        return redirect('/static/icons/xd.png')
    except:
        raise Http404("Apple touch icon not found")
