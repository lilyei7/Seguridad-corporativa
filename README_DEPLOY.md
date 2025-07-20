# 🔐 Security Corp - Sistema de Seguridad Corporativa

Sistema completo de gestión de seguridad corporativa con interfaz móvil PWA.

## 🚀 Despliegue en Servidor Linux (IP: 200.234.239.212)

### Opción 1: Despliegue Completo con Nginx + Gunicorn

```bash
# En el servidor Linux como root:
wget https://raw.githubusercontent.com/lilyei7/Seguridad-corporativa/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### Opción 2: Despliegue Rápido para Desarrollo

```bash
# En el servidor Linux como root:
wget https://raw.githubusercontent.com/lilyei7/Seguridad-corporativa/main/quick_deploy.sh
chmod +x quick_deploy.sh
./quick_deploy.sh

# Ejecutar manualmente:
cd /var/www/security_corp
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Opción 3: Instalación Manual Paso a Paso

```bash
# 1. Actualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependencias
sudo apt install -y python3 python3-pip python3-venv git nginx

# 3. Crear directorio del proyecto
sudo mkdir -p /var/www/security_corp
cd /var/www/security_corp

# 4. Clonar repositorio
sudo git clone https://github.com/lilyei7/Seguridad-corporativa.git .

# 5. Crear entorno virtual
sudo python3 -m venv venv
sudo venv/bin/activate

# 6. Instalar dependencias Python
sudo venv/bin/pip install -r requirements.txt

# 7. Configurar base de datos
sudo venv/bin/python manage.py makemigrations
sudo venv/bin/python manage.py migrate

# 8. Crear superusuario
sudo venv/bin/python manage.py createsuperuser

# 9. Recolectar archivos estáticos
sudo venv/bin/python manage.py collectstatic

# 10. Ejecutar servidor
sudo venv/bin/python manage.py runserver 0.0.0.0:8000
```

## 🌐 URLs de Acceso

- **Aplicación Principal**: http://200.234.239.212:8000/
- **Panel de Administración**: http://200.234.239.212:8000/admin/
- **Dashboard**: http://200.234.239.212:8000/dashboard/

## 👤 Credenciales por Defecto

- **Usuario**: admin
- **Contraseña**: admin123
- **Email**: admin@securecorp.com

## 📱 Características

- ✅ **Interfaz Móvil PWA**: Optimizada para dispositivos móviles
- ✅ **Gestión de Visitantes**: Registro y control de acceso
- ✅ **Sistema de Mantenimiento**: Checklists y seguimiento
- ✅ **Gestión de Inquilinos**: Administración de locales
- ✅ **Control de Personal**: Vigilantes y turnos
- ✅ **Panel de Administración**: Dashboard completo
- ✅ **Responsive Design**: Funciona en móviles, tablets y desktop

## 🔧 Comandos Útiles

```bash
# Ver logs del servicio
sudo journalctl -u security_corp -f

# Reiniciar aplicación
sudo systemctl restart security_corp

# Ver estado del servicio
sudo systemctl status security_corp

# Actualizar código
cd /var/www/security_corp
sudo git pull origin main
sudo systemctl restart security_corp

# Ejecutar migraciones
cd /var/www/security_corp
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
sudo systemctl restart security_corp
```

## 🛠️ Configuración del Servidor

### Puertos Abiertos
- **Puerto 80**: HTTP (Nginx)
- **Puerto 8000**: Django Development Server
- **Puerto 22**: SSH

### Servicios Configurados
- **Nginx**: Servidor web y proxy reverso
- **Gunicorn**: Servidor WSGI para Django
- **PostgreSQL**: Base de datos (opcional)
- **SystemD**: Gestión de servicios

## 📋 Estructura del Proyecto

```
security_corp/
├── accounts/          # Gestión de usuarios
├── dashboard/         # Panel principal
├── guards/           # Gestión de vigilantes
├── maintenance/      # Sistema de mantenimiento
├── tenants/          # Gestión de inquilinos
├── visits/           # Control de visitas
├── templates/        # Templates HTML
├── static/           # Archivos estáticos
├── media/            # Archivos subidos
└── requirements.txt  # Dependencias
```

## 🔐 Seguridad

- CSRF Protection habilitado
- XSS Protection activado
- Headers de seguridad configurados
- Firewall UFW configurado
- SSL/HTTPS listo para configurar

## 📞 Soporte

Para problemas o dudas:
1. Revisar logs: `sudo journalctl -u security_corp -f`
2. Verificar estado: `sudo systemctl status security_corp`
3. Reiniciar servicios: `sudo systemctl restart security_corp nginx`

---

**🚀 ¡Tu sistema de seguridad corporativa está listo para usar en http://200.234.239.212!**
