#!/usr/bin/env python3
"""
Sample Face Generator for Ash Robot

This script creates simple placeholder face images for testing.
These are basic geometric faces - replace them with better designs later!

Usage:
    python3 create_sample_faces.py
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_simple_face(filename, expression):
    """
    Create a simple geometric face with the given expression.
    
    Args:
        filename: Output filename
        expression: Expression name (affects eyes and mouth)
    """
    # Create image with dark blue background
    img = Image.new('RGB', (480, 320), color='#2C3E50')
    draw = ImageDraw.Draw(img)
    
    # Face circle (light background)
    draw.ellipse([90, 40, 390, 280], fill='#ECF0F1', outline='#34495E', width=3)
    
    # Eyes position and shape vary by expression
    eye_configs = {
        'happy': {'y': 110, 'height': 40, 'pupil_y': 5},
        'sad': {'y': 120, 'height': 40, 'pupil_y': -5},
        'neutral': {'y': 115, 'height': 40, 'pupil_y': 0},
        'listening': {'y': 110, 'height': 50, 'pupil_y': 0},  # Larger eyes
        'speaking': {'y': 115, 'height': 35, 'pupil_y': 0},
        'thinking': {'y': 110, 'height': 40, 'pupil_y': -10},  # Looking up
        'error': {'y': 120, 'height': 40, 'pupil_y': 0},
    }
    
    eye_cfg = eye_configs.get(expression, eye_configs['neutral'])
    eye_y = eye_cfg['y']
    eye_h = eye_cfg['height']
    pupil_offset = eye_cfg['pupil_y']
    
    # Left eye
    draw.ellipse([140, eye_y, 190, eye_y + eye_h], fill='white', outline='#34495E', width=2)
    draw.ellipse([155, eye_y + 10 + pupil_offset, 175, eye_y + 30 + pupil_offset], fill='#2C3E50')
    
    # Right eye
    draw.ellipse([290, eye_y, 340, eye_y + eye_h], fill='white', outline='#34495E', width=2)
    draw.ellipse([305, eye_y + 10 + pupil_offset, 325, eye_y + 30 + pupil_offset], fill='#2C3E50')
    
    # Special eye effects
    if expression == 'error':
        # X eyes
        draw.line([145, eye_y + 5, 185, eye_y + eye_h - 5], fill='#E74C3C', width=4)
        draw.line([185, eye_y + 5, 145, eye_y + eye_h - 5], fill='#E74C3C', width=4)
        draw.line([295, eye_y + 5, 335, eye_y + eye_h - 5], fill='#E74C3C', width=4)
        draw.line([335, eye_y + 5, 295, eye_y + eye_h - 5], fill='#E74C3C', width=4)
    
    # Mouth varies by expression
    mouth_color = '#2C3E50'
    
    if expression == 'happy':
        # Smile
        draw.arc([180, 190, 300, 250], start=0, end=180, fill=mouth_color, width=6)
        draw.chord([180, 190, 300, 240], start=0, end=180, fill='#E74C3C')
    
    elif expression == 'sad':
        # Frown
        draw.arc([180, 200, 300, 260], start=180, end=360, fill=mouth_color, width=6)
    
    elif expression == 'neutral':
        # Straight line
        draw.line([190, 215, 290, 215], fill=mouth_color, width=5)
    
    elif expression == 'listening':
        # Small O shape
        draw.ellipse([220, 200, 260, 230], outline=mouth_color, width=5)
        # Add ear indicators
        draw.arc([60, 130, 100, 170], start=300, end=60, fill='#34495E', width=4)
        draw.arc([380, 130, 420, 170], start=120, end=240, fill='#34495E', width=4)
    
    elif expression == 'speaking':
        # Open mouth
        draw.ellipse([210, 195, 270, 235], fill='#34495E', outline=mouth_color, width=3)
        # Sound waves
        draw.arc([320, 180, 360, 220], start=90, end=270, fill='#3498DB', width=3)
        draw.arc([365, 175, 410, 225], start=90, end=270, fill='#3498DB', width=2)
    
    elif expression == 'thinking':
        # Wavy mouth (uncertain)
        points = [(190, 215), (210, 220), (230, 215), (250, 220), (270, 215), (290, 220)]
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=mouth_color, width=5)
        # Thought bubble
        draw.ellipse([330, 50, 370, 80], outline='#95A5A6', width=2)
        draw.ellipse([350, 75, 365, 90], outline='#95A5A6', width=2)
        draw.ellipse([360, 85, 370, 95], outline='#95A5A6', width=2)
    
    elif expression == 'error':
        # Surprised O
        draw.ellipse([215, 200, 265, 240], fill='#34495E', outline='#E74C3C', width=3)
    
    # Add label at bottom
    try:
        # Try to use a nice font
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except:
        font = ImageFont.load_default()
    
    label = expression.upper()
    # Calculate text position (center)
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (480 - text_width) // 2
    draw.text((text_x, 285), label, fill='#95A5A6', font=font)
    
    # Save
    img.save(filename)
    print(f"Created: {filename}")


def main():
    """
    Generate all 7 face expressions.
    """
    print("=" * 50)
    print("  Ash Face Generator")
    print("=" * 50)
    print()
    print("This will create 7 sample face images (480×320 PNG)")
    print("in the assets/faces/ directory.")
    print()
    print("NOTE: These are simple placeholder faces.")
    print("Replace them with better designs for production!")
    print()
    
    # Create output directory if it doesn't exist
    output_dir = "assets/faces"
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if files already exist
    expressions = ['happy', 'sad', 'neutral', 'listening', 'speaking', 'thinking', 'error']
    existing = [expr for expr in expressions if os.path.exists(f"{output_dir}/{expr}.png")]
    
    if existing:
        print(f"Warning: {len(existing)} file(s) already exist:")
        for expr in existing:
            print(f"  - {expr}.png")
        print()
        response = input("Overwrite existing files? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    # Generate all faces
    print()
    print("Generating faces...")
    for expression in expressions:
        filename = f"{output_dir}/{expression}.png"
        create_simple_face(filename, expression)
    
    print()
    print("=" * 50)
    print("  Complete!")
    print("=" * 50)
    print()
    print("Face images created in assets/faces/")
    print()
    print("Test them with:")
    print("  python3 src/face_display.py")
    print()
    print("These are simple placeholder faces.")
    print("Consider replacing them with:")
    print("  - AI-generated images (DALL-E, Midjourney)")
    print("  - Custom designs (Photoshop, Figma, Canva)")
    print("  - Hand-drawn artwork")
    print()


if __name__ == "__main__":
    main()

