#!/bin/bash

# Script simplificado para desarrollo rápido
# Usar cuando solo necesites probar la aplicación

echo "🚀 Despliegue rápido de Security Corp..."

# Variables
PROJECT_DIR="/var/www/security_corp"
VENV_DIR="$PROJECT_DIR/venv"

# Crear directorio y clonar
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Si no existe, clonar el repo
if [ ! -d ".git" ]; then
    git clone https://github.com/lilyei7/Seguridad-corporativa.git .
fi

# Instalar Python y pip si no existen
apt update
apt install -y python3 python3-pip python3-venv

# Crear entorno virtual
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install Django==5.2.4 django-crispy-forms crispy-bootstrap5 Pillow whitenoise gunicorn

# Crear directorios
mkdir -p logs media staticfiles run

# Configurar permisos básicos
chmod -R 755 $PROJECT_DIR

# Ejecutar migraciones con SQLite
python manage.py makemigrations
python manage.py migrate

# Recolectar estáticos
python manage.py collectstatic --noinput

# Crear superusuario
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell

echo "✅ Configuración básica completada!"
echo "🚀 Para ejecutar el servidor:"
echo "cd $PROJECT_DIR && source venv/bin/activate && python manage.py runserver 0.0.0.0:8000"
