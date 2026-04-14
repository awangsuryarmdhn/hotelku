import os
from PIL import Image, ImageDraw, ImageFont

# Create directory
os.makedirs('static/icons', exist_ok=True)

def create_icon(size):
    # Create image with brand color
    img = Image.new('RGB', (size, size), color=(14, 165, 233)) # Manta Teal
    d = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default font
    try:
        font = ImageFont.truetype("arial", int(size * 0.5))
    except (IOError, OSError):
        font = ImageFont.load_default()

    # Draw 'M' in the center
    text = "M"
    # To center text, need to find bbox if supported
    try:
        bbox = d.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
    except AttributeError:
        # Pillow < 8.0 support
        w, h = d.textsize(text, font=font)

    d.text(((size-w)/2, (size-h)/2 - (size*0.05)), text, fill=(254, 252, 232), font=font)
    
    img.save(f'static/icons/icon-{size}.png')
    print(f'Generated icon-{size}.png')

create_icon(192)
create_icon(512)
