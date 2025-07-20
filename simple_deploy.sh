#!/bin/bash

echo "🚀 Despliegue simple de Security Corp con SQLite"

# Variables
PROJECT_DIR="/var/www/security_corp"
REPO_URL="https://github.com/lilyei7/Seguridad-corporativa.git"

echo "📦 Instalando dependencias del sistema..."
apt update
apt install -y python3 python3-pip python3-venv git

echo "📁 Clonando repositorio..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Clonar el repositorio
git clone $REPO_URL .

echo "🐍 Configurando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📁 Creando directorios necesarios..."
mkdir -p logs media staticfiles run

echo "📊 La base de datos SQLite ya viene en el repositorio, no hay que hacer migraciones"

echo "📁 Recolectando archivos estáticos..."
DJANGO_SETTINGS_MODULE=security_corp.settings_production python manage.py collectstatic --noinput

echo "🔐 Configurando permisos..."
chmod -R 755 $PROJECT_DIR

echo "✅ ¡Despliegue completado!"
echo ""
echo "🚀 Para ejecutar el servidor:"
echo "cd $PROJECT_DIR"
echo "source venv/bin/activate"
echo "DJANGO_SETTINGS_MODULE=security_corp.settings_production python manage.py runserver 0.0.0.0:8000"
echo ""
echo "🌐 Tu aplicación estará en: http://200.234.239.212:8000"
echo "🔑 Usa las mismas credenciales que ya tienes en tu base de datos SQLite"
