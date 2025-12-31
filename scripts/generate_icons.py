from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, path):
    # Create a gradient-like background
    img = Image.new('RGB', (size, size), color='#6366f1')
    d = ImageDraw.Draw(img)
    
    # Draw a simple "T" or logo shape
    # Center circle
    center = size // 2
    r = size // 3
    d.ellipse([center-r, center-r, center+r, center+r], fill='#4f46e5')
    
    # Text
    try:
        # Basic representation since we might not have fonts
        d.rectangle([center-r//2, center-r//2, center+r//2, center+r//2], fill='#ffffff')
    except:
        pass

    img.save(path)
    print(f"Created {path}")

sizes = [72, 96, 128, 144, 152, 192, 384, 512]
base_dir = r"e:\yngi loyihalar\TrendoAi\static\icons"

if not os.path.exists(base_dir):
    os.makedirs(base_dir)

for s in sizes:
    create_icon(s, os.path.join(base_dir, f"icon-{s}x{s}.png"))
