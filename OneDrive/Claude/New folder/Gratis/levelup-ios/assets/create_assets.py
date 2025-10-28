#!/usr/bin/env python3
"""
Generate required image assets for LevelUp iOS app
Creates: icon.png, splash.png, adaptive-icon.png, favicon.png
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_gradient_circle(size, color1, color2):
    """Create a circular gradient image"""
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Create gradient background
    for i in range(size[1]):
        ratio = i / size[1]
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, i), (size[0], i)], fill=(r, g, b))

    return image

def create_app_icon():
    """Create app icon (1024x1024)"""
    size = (1024, 1024)

    # Purple to light purple gradient
    color1 = (124, 58, 237)  # #7C3AED
    color2 = (167, 139, 250)  # #A78BFA

    image = create_gradient_circle(size, color1, color2)
    draw = ImageDraw.Draw(image)

    # Draw a level-up arrow/chevron symbol
    # Main arrow pointing up
    arrow_points = [
        (512, 200),   # Top point
        (700, 450),   # Right middle
        (650, 450),   # Right inner
        (512, 300),   # Top inner
        (374, 450),   # Left inner
        (324, 450),   # Left middle
    ]
    draw.polygon(arrow_points, fill='white')

    # Second arrow for "level up" effect
    arrow_points2 = [
        (512, 500),
        (700, 750),
        (650, 750),
        (512, 600),
        (374, 750),
        (324, 750),
    ]
    draw.polygon(arrow_points2, fill=(255, 255, 255, 200))

    # Add "LVL UP" text
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        font = ImageFont.load_default()

    text = "LEVEL UP"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size[0] - text_width) // 2, 820)

    # Add shadow
    draw.text((position[0] + 3, position[1] + 3), text, font=font, fill=(0, 0, 0, 100))
    # Add main text
    draw.text(position, text, font=font, fill='white')

    image.save('icon.png', 'PNG')
    print("[OK] Created icon.png (1024x1024)")

def create_adaptive_icon():
    """Create Android adaptive icon (1024x1024)"""
    # For adaptive icons, keep content within safe zone (66% of canvas)
    size = (1024, 1024)
    safe_zone = 676  # 66% of 1024
    margin = (1024 - safe_zone) // 2

    color1 = (124, 58, 237)  # #7C3AED
    color2 = (167, 139, 250)  # #A78BFA

    image = create_gradient_circle(size, color1, color2)
    draw = ImageDraw.Draw(image)

    # Draw simplified icon that fits in safe zone
    # Single centered arrow
    center = 512
    arrow_size = 250

    arrow_points = [
        (center, center - arrow_size),           # Top
        (center + arrow_size//2, center),        # Right
        (center + arrow_size//4, center),        # Right inner
        (center, center - arrow_size//2),        # Top inner
        (center - arrow_size//4, center),        # Left inner
        (center - arrow_size//2, center),        # Left
    ]
    draw.polygon(arrow_points, fill='white')

    # Second smaller arrow
    arrow_points2 = [
        (center, center),
        (center + arrow_size//2, center + arrow_size),
        (center + arrow_size//4, center + arrow_size),
        (center, center + arrow_size//2),
        (center - arrow_size//4, center + arrow_size),
        (center - arrow_size//2, center + arrow_size),
    ]
    draw.polygon(arrow_points2, fill=(255, 255, 255, 180))

    image.save('adaptive-icon.png', 'PNG')
    print("[OK] Created adaptive-icon.png (1024x1024)")

def create_splash_screen():
    """Create splash screen (1284x2778 for iPhone 12 Pro Max)"""
    size = (1284, 2778)

    color1 = (124, 58, 237)  # #7C3AED
    color2 = (167, 139, 250)  # #A78BFA

    image = create_gradient_circle(size, color1, color2)
    draw = ImageDraw.Draw(image)

    # Draw large centered logo
    center_x = size[0] // 2
    center_y = size[1] // 2

    # Large arrow
    arrow_size = 300
    arrow_points = [
        (center_x, center_y - arrow_size),
        (center_x + arrow_size//1.5, center_y),
        (center_x + arrow_size//3, center_y),
        (center_x, center_y - arrow_size//2),
        (center_x - arrow_size//3, center_y),
        (center_x - arrow_size//1.5, center_y),
    ]
    draw.polygon(arrow_points, fill='white')

    # Second arrow
    arrow_points2 = [
        (center_x, center_y + 50),
        (center_x + arrow_size//1.5, center_y + arrow_size + 50),
        (center_x + arrow_size//3, center_y + arrow_size + 50),
        (center_x, center_y + arrow_size//2 + 50),
        (center_x - arrow_size//3, center_y + arrow_size + 50),
        (center_x - arrow_size//1.5, center_y + arrow_size + 50),
    ]
    draw.polygon(arrow_points2, fill=(255, 255, 255, 200))

    # Add app name
    try:
        font_large = ImageFont.truetype("arial.ttf", 120)
        font_small = ImageFont.truetype("arial.ttf", 60)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Main title
    text = "LEVEL UP"
    bbox = draw.textbbox((0, 0), text, font=font_large)
    text_width = bbox[2] - bbox[0]
    position = ((size[0] - text_width) // 2, center_y + arrow_size + 200)

    draw.text((position[0] + 4, position[1] + 4), text, font=font_large, fill=(0, 0, 0, 100))
    draw.text(position, text, font=font_large, fill='white')

    # Tagline
    tagline = "Transform Your Life Into A Game"
    bbox = draw.textbbox((0, 0), tagline, font=font_small)
    text_width = bbox[2] - bbox[0]
    position = ((size[0] - text_width) // 2, center_y + arrow_size + 350)

    draw.text(position, tagline, font=font_small, fill=(255, 255, 255, 220))

    image.save('splash.png', 'PNG')
    print("[OK] Created splash.png (1284x2778)")

def create_favicon():
    """Create favicon (48x48)"""
    size = (48, 48)

    color1 = (124, 58, 237)
    color2 = (167, 139, 250)

    image = create_gradient_circle(size, color1, color2)
    draw = ImageDraw.Draw(image)

    # Simple small arrow
    arrow_points = [
        (24, 10),
        (35, 24),
        (30, 24),
        (24, 17),
        (18, 24),
        (13, 24),
    ]
    draw.polygon(arrow_points, fill='white')

    # Second small arrow
    arrow_points2 = [
        (24, 24),
        (35, 38),
        (30, 38),
        (24, 31),
        (18, 38),
        (13, 38),
    ]
    draw.polygon(arrow_points2, fill=(255, 255, 255, 180))

    image.save('favicon.png', 'PNG')
    print("[OK] Created favicon.png (48x48)")

if __name__ == '__main__':
    print("Creating LevelUp app assets...")
    print("-" * 40)

    try:
        create_app_icon()
        create_adaptive_icon()
        create_splash_screen()
        create_favicon()
        print("-" * 40)
        print("[SUCCESS] All assets created successfully!")
        print("\nGenerated files:")
        print("  - icon.png (1024x1024) - App icon")
        print("  - adaptive-icon.png (1024x1024) - Android adaptive icon")
        print("  - splash.png (1284x2778) - Splash screen")
        print("  - favicon.png (48x48) - Web favicon")
    except Exception as e:
        print(f"[ERROR] Error creating assets: {e}")
        import traceback
        traceback.print_exc()
