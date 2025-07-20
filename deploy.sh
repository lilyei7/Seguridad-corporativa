#!/bin/bash

# Script de despliegue para Security Corp
# Ejecutar como root en el servidor

set -e

PROJECT_NAME="security_corp"
PROJECT_DIR="/var/www/security_corp"
REPO_URL="https://github.com/lilyei7/Seguridad-corporativa.git"
VENV_DIR="$PROJECT_DIR/venv"

echo "🚀 Iniciando despliegue de Security Corp..."

# Actualizar sistema
echo "📦 Actualizando sistema..."
apt update
apt upgrade -y

# Instalar dependencias del sistema
echo "🔧 Instalando dependencias..."
apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git

# Crear usuario para la aplicación si no existe
if ! id "www-data" &>/dev/null; then
    useradd --system --gid www-data --shell /bin/bash --home $PROJECT_DIR www-data
fi

# Crear directorio del proyecto
echo "📁 Creando directorio del proyecto..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Clonar o actualizar repositorio
if [ -d ".git" ]; then
    echo "🔄 Actualizando repositorio..."
    git pull origin main
else
    echo "📥 Clonando repositorio..."
    git clone $REPO_URL .
fi

# Crear entorno virtual
echo "🐍 Configurando entorno virtual..."
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Instalar dependencias de Python
echo "📦 Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Configurar base de datos PostgreSQL
echo "🗄️ Configurando base de datos..."
sudo -u postgres psql -c "CREATE DATABASE security_corp;" || echo "Base de datos ya existe"
sudo -u postgres psql -c "CREATE USER security_user WITH PASSWORD 'security_pass';" || echo "Usuario ya existe"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE security_corp TO security_user;"

# Variables de entorno
echo "🔐 Configurando variables de entorno..."
export DJANGO_SETTINGS_MODULE=security_corp.settings_production
export DB_NAME=security_corp
export DB_USER=security_user
export DB_PASSWORD=security_pass
export DB_HOST=localhost
export DB_PORT=5432

# Crear directorios necesarios
mkdir -p logs
mkdir -p run
mkdir -p media
mkdir -p staticfiles

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
python manage.py makemigrations
python manage.py migrate

# Recolectar archivos estáticos
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Crear superusuario si no existe
echo "👤 Creando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@securecorp.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"

# Configurar permisos
echo "🔐 Configurando permisos..."
chown -R www-data:www-data $PROJECT_DIR
chmod +x $PROJECT_DIR/gunicorn_start.sh

# Configurar Gunicorn como servicio
echo "⚙️ Configurando servicio Gunicorn..."
cat > /etc/systemd/system/security_corp.service << EOF
[Unit]
Description=Security Corp gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/security_corp
ExecStart=/var/www/security_corp/gunicorn_start.sh
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Configurar Nginx
echo "🌐 Configurando Nginx..."
cp nginx_security_corp.conf /etc/nginx/sites-available/security_corp
ln -sf /etc/nginx/sites-available/security_corp /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Probar configuración de Nginx
nginx -t

# Iniciar servicios
echo "🚀 Iniciando servicios..."
systemctl daemon-reload
systemctl enable security_corp
systemctl start security_corp
systemctl enable nginx
systemctl restart nginx

# Configurar firewall
echo "🔥 Configurando firewall..."
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

echo "✅ ¡Despliegue completado!"
echo "📱 Tu aplicación está disponible en: http://200.234.239.212"
echo "🔑 Superusuario: admin / admin123"
echo "🌐 Panel admin: http://200.234.239.212/admin/"

echo "📋 Comandos útiles:"
echo "- Ver logs: sudo journalctl -u security_corp -f"
echo "- Reiniciar app: sudo systemctl restart security_corp"
echo "- Reiniciar nginx: sudo systemctl restart nginx"
echo "- Ver estado: sudo systemctl status security_corp"
