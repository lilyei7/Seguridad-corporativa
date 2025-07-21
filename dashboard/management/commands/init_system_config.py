from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import SystemThemeConfiguration


class Command(BaseCommand):
    help = 'Inicializa la configuración del sistema con valores por defecto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--company-name',
            type=str,
            default='Corporativo Aqua Administración',
            help='Nombre de la empresa (por defecto: Corporativo Aqua Administración)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar creación aunque ya exista una configuración',
        )

    def handle(self, *args, **options):
        company_name = options['company_name']
        force = options['force']
        
        self.stdout.write('Inicializando configuración del sistema...')
        
        # Verificar si ya existe una configuración
        existing_config = SystemThemeConfiguration.objects.filter(is_active=True).first()
        
        if existing_config and not force:
            self.stdout.write(
                self.style.WARNING(
                    f'Ya existe una configuración activa: "{existing_config.company_name}"'
                )
            )
            self.stdout.write('Use --force para sobrescribir la configuración existente')
            return
        
        # Obtener usuario administrador
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(
                self.style.ERROR(
                    'No se encontró un usuario administrador. Cree un superusuario primero.'
                )
            )
            return
        
        # Desactivar configuraciones existentes si se usa --force
        if force and existing_config:
            SystemThemeConfiguration.objects.filter(is_active=True).update(is_active=False)
            self.stdout.write(
                self.style.WARNING(f'Configuración anterior desactivada: "{existing_config.company_name}"')
            )
        
        # Crear nueva configuración
        new_config = SystemThemeConfiguration.objects.create(
            company_name=company_name,
            theme='default',
            dark_mode=False,
            primary_color='#0ea5e9',
            secondary_color='#0284c7',
            accent_color='#0369a1',
            sidebar_color='#1e293b',
            created_by=admin_user,
            is_active=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Configuración del sistema creada exitosamente!'
            )
        )
        self.stdout.write(f'   📝 Nombre de empresa: "{new_config.company_name}"')
        self.stdout.write(f'   🎨 Tema: {new_config.get_theme_display()}')
        self.stdout.write(f'   👤 Creado por: {new_config.created_by.username}')
        self.stdout.write(f'   📅 Fecha: {new_config.created_at.strftime("%d/%m/%Y %H:%M")}')
        
        # Mostrar información para el usuario
        self.stdout.write('\n' + '='*60)
        self.stdout.write('🎯 PRÓXIMOS PASOS:')
        self.stdout.write('1. Ir a http://127.0.0.1:8000/dashboard/config/ para editar la configuración')
        self.stdout.write('2. Subir logo de la empresa')
        self.stdout.write('3. Personalizar colores y tema')
        self.stdout.write('4. Los cambios se aplicarán automáticamente en el sidebar')
        self.stdout.write('='*60)
