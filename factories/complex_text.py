from moviepy.editor import TextClip
from PIL import Image, ImageOps
import numpy as np
import os

def render_complex_text_to_pil(text: str, font_path: str, font_size: int, color: str) -> Image.Image:
    """
    Renders complex text using a luma-masking technique for robustness.
    1. Render Black text on White background (Proven to work).
    2. Invert to get Alpha Mask.
    3. Apply this mask to a solid canvas of the desired color.
    """
    try:
        # Sanitize path for ImageMagick (Forward slashes required on Windows sometimes)
        font_path = font_path.replace("\\", "/")
        
        # 1. Render Black text on White background
        clip_mask = TextClip(text, font=font_path, fontsize=font_size, color='black', bg_color='white')
        mask_frame = clip_mask.get_frame(0) # RGB
        
        # 2. Convert to PIL and Invert to get Alpha
        pil_img = Image.fromarray(mask_frame).convert('L')
        pil_mask = ImageOps.invert(pil_img)
        
        # 3. Create Solid Color Image
        w, h = pil_mask.size
        
        # Parse color string/tuple to RGB tuple for PIL
        pil_color = color
        if isinstance(color, str) and color.startswith("rgb("):
             try:
                 parts = color.replace("rgb(", "").replace(")", "").split(",")
                 pil_color = tuple(int(x) for x in parts)
             except:
                 pil_color = (0, 0, 0)
        
        # Create solid image of the desired text color
        solid_color_img = Image.new('RGB', (w, h), pil_color)
        
        # Add the alpha channel from the mask
        solid_color_img.putalpha(pil_mask)
        
        return solid_color_img

    except Exception as e:
        print(f"[WARNING] Complex text rendering failed: {e}. Falling back to PIL default.")
        from PIL import ImageDraw, ImageFont
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()
            
        dummy = Image.new('RGBA', (1, 1))
        d = ImageDraw.Draw(dummy)
        bbox = d.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        img = Image.new('RGBA', (w + 20, h + 20), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((10, 10), text, font=font, fill=color)
        return img
