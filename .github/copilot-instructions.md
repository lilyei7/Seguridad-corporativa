<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# SecureCorp Admin - Sistema de Seguridad Corporativa

Este es un proyecto Django para la gestión de seguridad corporativa que incluye:

## Estructura del Proyecto

- **accounts**: Gestión de usuarios y autenticación
- **tenants**: Gestión de inquilinos del corporativo  
- **guards**: Gestión de vigilantes y turnos
- **visits**: Sistema de registro y control de visitas
- **dashboard**: Panel de administración y vistas principales

## Tecnologías Utilizadas

- **Backend**: Django 5.2.4
- **Frontend**: Tailwind CSS, Alpine.js
- **Base de datos**: SQLite (desarrollo)
- **Autenticación**: Django Auth

## Guías de Desarrollo

### Modelos
- Utilizar verbose_name en español para todos los campos
- Incluir created_at y updated_at en modelos principales
- Usar choices para campos con opciones limitadas
- Implementar métodos __str__ descriptivos

### Vistas
- Todas las vistas requieren @login_required
- Usar class-based views para operaciones CRUD
- Implementar filtros y búsquedas en listas
- Mostrar mensajes de éxito/error al usuario

### Templates
- Usar Tailwind CSS para todos los estilos
- Mantener consistencia en el diseño siguiendo el theme principal
- Incluir iconos de Font Awesome
- Hacer responsive todas las interfaces

### Formularios
- Usar widgets personalizados con clases de Tailwind
- Validaciones en español
- Campos opcionales claramente marcados
- Usar crispy-forms cuando sea necesario

## Configuración de Colores (Tailwind)

```javascript
colors: {
    'primary': {
        50: '#f0f9ff',
        500: '#0ea5e9', 
        600: '#0284c7',
        700: '#0369a1',
    },
    'sidebar': '#1e293b',
    'sidebar-hover': '#334155',
}
```

## URLs y Navegación

- Dashboard principal: `/dashboard/`
- Gestión de inquilinos: `/tenants/`
- Gestión de visitas: `/visits/`
- Gestión de vigilantes: `/guards/`
- Administración Django: `/admin/`

## Usuarios y Permisos

- Superusuario: admin@securecorp.com
- Los vigilantes pueden registrar visitas
- Los supervisores pueden aprobar visitas
- Sistema de grupos para diferentes niveles de acceso

## Estilo de Código

- Seguir PEP 8 para Python
- Usar nombres descriptivos en español para funciones y variables relacionadas con el negocio
- Comentarios en español
- Documentar funciones complejas
- Usar type hints cuando sea apropiado
