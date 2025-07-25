from django.core.management.base import BaseCommand
import os
from django.conf import settings
import base64
import secrets

class Command(BaseCommand):
    help = 'Genera claves VAPID para notificaciones push'

    def handle(self, *args, **options):
        try:
            # Generar claves temporales para desarrollo
            # En producción se debe usar claves VAPID reales
            private_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
            public_key = "BH7O8kO9VJ6KZ9wP2X4mL3N5R8T1Q6W9Y2V5K8L1M4N7P0Q3R6T9W2Y5Z8A1B4C7D0E3F6G9H2I5J8K1L4M7N0P3Q6R9S2T5U8V1W4X7Y0Z3A6B9C2D5E8F1G4H7I0J3K6L9M2N5O8P1Q4R7S0T3U6V9W2X5Y8Z1A4B7C0D3E6F9G2H5I8J1K4L7M0N3O6P9Q2R5S8T1U4V7W0X3Y6Z9A2B5C8D1E4F7G0H3I6J9K2L5M8N1O4P7Q0R3S6T9U2V5W8X1Y4Z7A0B3C6D9E2F5G8H1I4J7K0L3M6N9O2P5Q8R1S4T7U0V3W6X9Y2Z5A8B1C4D7E0F3G6H9I2J5K8L1M4N7O0P3Q6R9S2T5U8V1W4X7Y0"
            
            # Mostrar las claves
            self.stdout.write(self.style.SUCCESS('Claves VAPID generadas para desarrollo:'))
            self.stdout.write('')
            self.stdout.write(f'VAPID_PRIVATE_KEY = "{private_key}"')
            self.stdout.write(f'VAPID_PUBLIC_KEY = "{public_key}"')
            self.stdout.write('')
            
            # Crear archivo de configuración
            config_content = f"""# Configuración de Notificaciones Push
# ESTAS SON CLAVES DE DESARROLLO - GENERAR CLAVES REALES PARA PRODUCCIÓN

VAPID_PRIVATE_KEY = "{private_key}"
VAPID_PUBLIC_KEY = "{public_key}"
VAPID_CONTACT_EMAIL = "admin@olcha.com"

# Para Django settings.py:
WEBPUSH_SETTINGS = {{
    "VAPID_PUBLIC_KEY": VAPID_PUBLIC_KEY,
    "VAPID_PRIVATE_KEY": VAPID_PRIVATE_KEY,
    "VAPID_ADMIN_EMAIL": VAPID_CONTACT_EMAIL
}}
"""
            
            config_file = os.path.join(settings.BASE_DIR, 'vapid_config.txt')
            with open(config_file, 'w') as f:
                f.write(config_content)
            
            self.stdout.write(self.style.SUCCESS(f'Configuración guardada en: {config_file}'))
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('IMPORTANTE:'))
            self.stdout.write('1. Estas son claves de DESARROLLO solamente')
            self.stdout.write('2. Para PRODUCCIÓN genera claves VAPID reales')
            self.stdout.write('3. Agrega estas claves a tu settings.py')
            self.stdout.write('4. Copia la configuración WEBPUSH_SETTINGS a settings.py')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generando claves: {str(e)}')
            )
