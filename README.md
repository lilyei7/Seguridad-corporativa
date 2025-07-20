# SecureCorp Admin - Sistema de Seguridad Corporativa

Sistema integral de gestión de seguridad corporativa desarrollado con Django y Tailwind CSS.

## 🚀 Características

- **Gestión de Inquilinos**: Registro y administración de inquilinos del corporativo
- **Control de Visitas**: Sistema completo de registro, programación y seguimiento de visitas
- **Gestión de Vigilantes**: Administración del personal de seguridad y turnos
- **Panel de Administración**: Dashboard con estadísticas y acciones rápidas
- **Interfaz Moderna**: Diseño responsive con Tailwind CSS
- **Sistema de Autenticación**: Control de acceso por roles

## 🛠️ Tecnologías

- **Backend**: Django 5.2.4
- **Frontend**: Tailwind CSS, Alpine.js, Font Awesome
- **Base de datos**: SQLite (desarrollo)
- **Forms**: Django Crispy Forms con Bootstrap 5

## 📦 Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd "Seguridad corporativa"
```

2. **Crear y activar entorno virtual**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias**
```bash
pip install django pillow python-decouple whitenoise crispy-forms crispy-bootstrap5
```

4. **Configurar base de datos**
```bash
python manage.py migrate
```

5. **Crear superusuario**
```bash
python manage.py createsuperuser
```

6. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

## 🏗️ Estructura del Proyecto

```
security_corp/
├── accounts/          # Gestión de usuarios
├── tenants/           # Gestión de inquilinos
├── guards/            # Gestión de vigilantes
├── visits/            # Sistema de visitas
├── dashboard/         # Panel principal
├── templates/         # Templates HTML
├── static/           # Archivos estáticos
└── media/            # Archivos multimedia
```

## 📱 Funcionalidades Principales

### Panel de Administración (Dashboard)
- Estadísticas en tiempo real
- Visitas próximas
- Vigilantes activos
- Acciones rápidas

### Gestión de Inquilinos
- Registro de nuevos inquilinos
- Información de contacto
- Estado activo/inactivo
- Historial de visitas

### Sistema de Visitas
- Registro de visitantes
- Programación de visitas
- Control de entrada/salida
- Estados: Pendiente, En Progreso, Completada, Cancelada
- Registro de artículos

### Gestión de Vigilantes
- Registro de personal de seguridad
- Asignación de turnos
- Estados: Activo, Inactivo, Suspendido, Vacaciones
- Jerarquías: Vigilante, Supervisor, Jefe de Seguridad

## 🎨 Diseño e Interfaz

El sistema utiliza un diseño moderno basado en Tailwind CSS con:

- **Colores principales**: Azul corporativo (#0ea5e9)
- **Sidebar oscuro**: Navegación lateral fija
- **Cards y componentes**: Diseño limpio y profesional
- **Responsive**: Adaptable a dispositivos móviles
- **Iconografía**: Font Awesome para iconos consistentes

## 👥 Usuarios y Permisos

### Tipos de Usuario
- **Administrador**: Acceso completo al sistema
- **Supervisor**: Gestión de visitas y vigilantes
- **Vigilante**: Registro y control de visitas

### Credenciales por Defecto
- **Usuario**: admin
- **Email**: admin@securecorp.com
- **Contraseña**: Configurada durante la instalación

## 🔧 Configuración

### Variables de Entorno
Crear un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu-clave-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Configuración de Base de Datos
Por defecto usa SQLite. Para producción, configurar PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'securecorp_db',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📊 Modelos de Datos

### Inquilino (Tenant)
- Información de contacto
- Dirección completa
- Usuario asignado
- Estado activo/inactivo

### Visita (Visit)
- Datos del visitante
- Inquilino a visitar
- Programación y control de tiempos
- Artículos y vehículos
- Log de actividades

### Vigilante (Guard)
- Vinculado a usuario Django
- Información laboral
- Turnos de trabajo
- Contactos de emergencia

## 🚀 Despliegue

### Preparación para Producción
1. Configurar variables de entorno
2. Usar base de datos PostgreSQL
3. Configurar servidor web (Nginx + Gunicorn)
4. Configurar archivos estáticos con WhiteNoise

### Comandos de Despliegue
```bash
python manage.py collectstatic
python manage.py migrate
python manage.py createsuperuser
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear branch para nueva característica (`git checkout -b feature/nueva-caracteristica`)
3. Commit los cambios (`git commit -am 'Agregar nueva característica'`)
4. Push al branch (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

Para soporte técnico o consultas:
- Email: admin@securecorp.com
- Documentación: `/admin/doc/`

---

© 2025 SecureCorp Admin. Sistema de Gestión de Seguridad Corporativa.
