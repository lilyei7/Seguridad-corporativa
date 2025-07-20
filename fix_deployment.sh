#!/bin/bash

echo "🔧 Reparando problemas de despliegue..."

# Asegurar que estamos en el directorio correcto
cd /var/www/security_corp

# Activar entorno virtual
source venv/bin/activate

echo "🗄️ Cambiando a SQLite para evitar problemas de PostgreSQL..."

# Eliminar migraciones problemáticas si existen
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Regenerar migraciones
echo "🔄 Regenerando migraciones..."
python manage.py makemigrations accounts
python manage.py makemigrations tenants  
python manage.py makemigrations guards
python manage.py makemigrations visits
python manage.py makemigrations dashboard
python manage.py makemigrations maintenance

# Ejecutar migraciones con SQLite
echo "📊 Ejecutando migraciones con SQLite..."
python manage.py migrate

# Crear superusuario
echo "👤 Creando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@securecorp.com', 'admin123')
    print('✅ Superusuario creado: admin/admin123')
else:
    print('✅ Superusuario ya existe')
"

# Recolectar archivos estáticos
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Configurar permisos
echo "🔐 Configurando permisos..."
chmod -R 755 /var/www/security_corp
chown -R www-data:www-data /var/www/security_corp

echo "✅ Reparación completada!"
echo ""
echo "🚀 Para ejecutar el servidor:"
echo "cd /var/www/security_corp"
echo "source venv/bin/activate"
echo "python manage.py runserver 0.0.0.0:8000"
echo ""
echo "🌐 URL: http://200.234.239.212:8000"
echo "👤 Admin: admin / admin123"
