"""
Script to generate icon.png for HW Group integration.

This script creates a 256x256 PNG icon using PIL (Pillow).
If SVG support is available (cairosvg), it can convert the SVG template.
Otherwise, it creates a simple icon directly.

Usage:
    python generate_icon.py
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # Create a new image with transparent background
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw background circle with gradient effect (simplified as solid color)
    background_color = (0, 102, 204, 255)  # Blue #0066CC
    center = size // 2
    radius = 120
    
    # Draw main circle
    draw.ellipse([center-radius, center-radius, center+radius, center+radius], 
                 fill=background_color)
    
    # Draw device/server representation
    device_color = (255, 255, 255, 230)  # White with slight transparency
    draw.rounded_rectangle([70, 60, 186, 140], radius=8, fill=device_color)
    
    # Draw server lines
    line_color = (0, 102, 204, 255)
    draw.rounded_rectangle([80, 70, 176, 78], radius=2, fill=line_color)
    draw.rounded_rectangle([80, 88, 176, 96], radius=2, fill=line_color)
    draw.rounded_rectangle([80, 106, 176, 114], radius=2, fill=line_color)
    
    # Draw sensor circles
    sensor_positions = [(95, 170), (128, 170), (161, 170)]
    sensor_labels = ['T', 'H', 'V']
    
    for (x, y), label in zip(sensor_positions, sensor_labels):
        # Draw circle
        draw.ellipse([x-15, y-15, x+15, y+15], fill=device_color)
        
        # Draw label (simplified - text might not be perfectly centered without font)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Get text bbox for centering
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        draw.text((x - text_width//2, y - text_height//2 - 2), 
                  label, fill=line_color, font=font)
    
    # Draw "HWG" text at bottom
    try:
        large_font = ImageFont.truetype("arial.ttf", 28)
    except:
        large_font = ImageFont.load_default()
    
    text = "HWG"
    bbox = draw.textbbox((0, 0), text, font=large_font)
    text_width = bbox[2] - bbox[0]
    
    draw.text((center - text_width//2, 205), 
              text, fill=(255, 255, 255, 255), font=large_font)
    
    # Save the icon
    output_path = os.path.join('custom_components', 'hwgroup', 'icon.png')
    img.save(output_path, 'PNG')
    print(f"✅ Icon created successfully: {output_path}")
    print(f"   Size: {size}x{size} pixels")
    print(f"   Format: PNG with transparency")
    
except ImportError as e:
    print("❌ Error: PIL (Pillow) is required to generate the icon.")
    print("   Install it with: pip install Pillow")
    print(f"   Error details: {e}")
except Exception as e:
    print(f"❌ Error creating icon: {e}")
    print("\nAlternatively, you can:")
    print("1. Open icon_template.svg in a graphics editor")
    print("2. Export as PNG at 256x256 pixels")
    print("3. Save as custom_components/hwgroup/icon.png")
