from django.shortcuts import render
from django.http import HttpResponse

def test_notifications(request):
    """Vista para testing del sistema de notificaciones"""
    return render(request, 'test_notifications.html')
