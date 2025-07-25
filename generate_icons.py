"""
Script para generar íconos PNG para la PWA de SecureCorp
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Crear un ícono PNG con el símbolo de escudo"""
    
    # Crear imagen con fondo azul
    img = Image.new('RGBA', (size, size), (14, 165, 233, 255))  # #0ea5e9
    draw = ImageDraw.Draw(img)
    
    # Dibujar escudo blanco
    center = size // 2
    shield_size = size // 3
    
    # Puntos del escudo
    points = [
        (center, center - shield_size),  # Top
        (center - shield_size//2, center - shield_size//3),  # Left top
        (center - shield_size//2, center + shield_size//4),  # Left bottom
        (center, center + shield_size),  # Bottom
        (center + shield_size//2, center + shield_size//4),  # Right bottom
        (center + shield_size//2, center - shield_size//3),  # Right top
    ]
    
    # Dibujar escudo
    draw.polygon(points, fill=(255, 255, 255, 255))
    
    # Dibujar marca de verificación
    check_size = shield_size // 3
    check_points = [
        (center - check_size//2, center),
        (center - check_size//4, center + check_size//3),
        (center + check_size//2, center - check_size//3)
    ]
    
    for i in range(len(check_points) - 1):
        draw.line([check_points[i], check_points[i+1]], fill=(14, 165, 233, 255), width=max(2, size//50))
    
    # Guardar imagen
    img.save(filename, 'PNG')
    print(f"✅ Ícono creado: {filename} ({size}x{size})")

def main():
    """Generar todos los íconos necesarios"""
    
    # Crear directorio si no existe
    icons_dir = 'static/icons'
    os.makedirs(icons_dir, exist_ok=True)
    
    # Tamaños de íconos requeridos
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    print("🎨 Generando íconos PNG para SecureCorp PWA...")
    
    for size in sizes:
        filename = f"{icons_dir}/icon-{size}.png"
        create_icon(size, filename)
    
    print("🎉 ¡Todos los íconos generados exitosamente!")
    print("\nÍconos creados:")
    for size in sizes:
        print(f"  - icon-{size}.png ({size}x{size})")

if __name__ == "__main__":
    main()
