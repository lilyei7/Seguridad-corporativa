# CREDENCIALES DEL SISTEMA - OLCHA TECNOLOGÍA EN SEGURIDAD

## 🔧 Información del Sistema
- **URL Local**: http://127.0.0.1:8000/
- **Panel de Administración Django**: http://127.0.0.1:8000/admin/
- **Empresa**: Olcha Tecnología En Seguridad

## 👥 TIPOS DE USUARIO Y ACCESOS

### 🔴 ADMINISTRADOR (Acceso Total)
- **Usuario**: `admin`
- **Contraseña**: `admin123`
- **Permisos**: Acceso completo al sistema
- **Panel**: Panel de Administración - Gestión completa de inquilinos, vigilantes, visitas y configuración

### 🟢 VIGILANTES (Control de Accesos)
- **Usuario**: `vigilante1` | **Contraseña**: `vigilante123`
- **Usuario**: `vigilante2` | **Contraseña**: `vigilante123`
- **Permisos**: Gestión de visitas, aprobación de accesos, reportes de incidentes
- **Panel**: Panel de Vigilancia - Control de accesos y gestión de visitas en tiempo real

### 🟣 INQUILINOS (Gestión de Local)
- **Usuario**: `inquilino1` | **Contraseña**: `inquilino123` (Farmacia San José)
- **Usuario**: `inquilino2` | **Contraseña**: `inquilino123` (Consultorio Dental)
- **Permisos**: Gestión de visitas a su local, registro de personal autorizado
- **Panel**: Panel de Inquilino - Gestión de visitas y accesos a su local específico

## 🎯 CARACTERÍSTICAS PRINCIPALES

### Panel de Administración
- Gestión completa de inquilinos y locales
- Control total del personal de seguridad
- Supervisión de todas las visitas
- Reportes y estadísticas generales
- Configuración del sistema

### Panel de Vigilancia
- Lista de visitas pendientes de aprobación
- Control de accesos en tiempo real
- Registro de llegadas y salidas
- Gestión de visitantes sin cita previa
- Reportes de incidentes de seguridad

### Panel de Inquilino
- Registro de nuevas visitas
- Visualización de visitas programadas
- Gestión de personal autorizado
- Historial de accesos al local
- Información del local asignado

## 🚀 FUNCIONALIDADES POR TIPO DE USUARIO

| Funcionalidad | Admin | Vigilante | Inquilino |
|--------------|-------|-----------|-----------|
| Ver todas las visitas | ✅ | ✅ | ❌ |
| Aprobar/Rechazar visitas | ✅ | ✅ | ❌ |
| Crear visitas | ✅ | ✅ | ✅ |
| Ver mis visitas | ✅ | ❌ | ✅ |
| Gestión de inquilinos | ✅ | ❌ | ❌ |
| Gestión de vigilantes | ✅ | ❌ | ❌ |
| Reportar incidentes | ✅ | ✅ | ❌ |
| Panel de administración Django | ✅ | ❌ | ❌ |

## 📝 Notas Importantes

1. **Login Inteligente**: El sistema detecta automáticamente el tipo de usuario y lo redirige a su panel correspondiente
2. **Diseño Responsivo**: Interfaz optimizada siguiendo el diseño corporativo solicitado
3. **Navegación Contextual**: Cada tipo de usuario ve solo las opciones relevantes a su rol
4. **Tiempo Real**: Los vigilantes pueden ver actualizaciones de visitas en tiempo real

## 🔄 Para Iniciar el Servidor

```bash
# Activar entorno virtual
.\.venv\Scripts\activate

# Iniciar servidor de desarrollo
python manage.py runserver
```

## 📞 Soporte
Para soporte técnico o configuraciones adicionales, contactar al administrador del sistema.

---
**Sistema Desarrollado para Olcha Tecnología En Seguridad**  
*Control de Accesos Corporativo v1.0*
