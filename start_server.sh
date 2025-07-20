#!/bin/bash

echo "🚀 Iniciando servidor Security Corp..."

cd /var/www/security_corp
source venv/bin/activate

echo "🌐 Servidor ejecutándose en http://200.234.239.212:8000"
echo "🛑 Presiona Ctrl+C para detener el servidor"

DJANGO_SETTINGS_MODULE=security_corp.settings_production python manage.py runserver 0.0.0.0:8000
