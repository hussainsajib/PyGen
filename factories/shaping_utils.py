import os
import logging
import uharfbuzz as hb
import freetype
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)

def render_shaped_text(text: str, font_path: str, font_size: int, color: str or tuple) -> Image.Image:
    """
    Renders complex text (Bengali, Arabic, etc.) manually using HarfBuzz and FreeType.
    This works even if Pillow is not compiled with libraqm.
    """
    try:
        # 1. Shape the text with HarfBuzz
        with open(font_path, 'rb') as f:
            font_data = f.read()
        
        face = hb.Face(font_data)
        font = hb.Font(face)
        # Scale is in 1/64 pixels, so font_size * 64
        font.scale = (font_size * 64, font_size * 64)
        
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf)
        
        infos = buf.glyph_infos
        positions = buf.glyph_positions
        
        # 2. Render glyphs with FreeType
        ft_face = freetype.Face(font_path)
        ft_face.set_char_size(font_size * 64)
        
        # Calculate bounding box
        min_x, min_y, max_x, max_y = 0, 0, 0, 0
        x_cursor = 0
        y_cursor = 0
        
        # We need a more accurate bbox. HarfBuzz gives advances.
        for info, pos in zip(infos, positions):
            # Advance is in 1/64th of a pixel
            x_cursor += pos.x_advance / 64.0
            y_cursor += pos.y_advance / 64.0
            
        # For vertical metrics
        ascent = ft_face.size.ascender / 64.0
        descent = ft_face.size.descender / 64.0
        height = ascent - descent
        
        width = int(x_cursor) + 20 # Add horizontal padding
        canvas_height = int(height) + 20
        
        # 3. Draw to Pillow
        img = Image.new('RGBA', (width, canvas_height), (0, 0, 0, 0))
        
        # Parse color
        if isinstance(color, str):
            if color.startswith("#"):
                color = color.lstrip("#")
                if len(color) == 3: color = "".join([c*2 for c in color])
                color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            elif color.startswith("rgb("):
                color = tuple(int(x) for x in color.replace("rgb(", "").replace(")", "").split(","))
            else:
                color = (255, 255, 255) # Default white
        
        x_offset = 10
        y_baseline = ascent + 10
        
        for info, pos in zip(infos, positions):
            glyph_id = info.codepoint
            ft_face.load_glyph(glyph_id, freetype.FT_LOAD_DEFAULT | freetype.FT_LOAD_RENDER)
            bitmap = ft_face.glyph.bitmap
            
            # The bitmap is a coverage mask (grayscale)
            if bitmap.width > 0 and bitmap.rows > 0:
                # Convert bitmap buffer to a PIL image
                glyph_mask = Image.frombytes('L', (bitmap.width, bitmap.rows), bytes(bitmap.buffer))
                
                # Calculate placement
                # ft_face.glyph.bitmap_left is distance from cursor to left edge of bitmap
                # ft_face.glyph.bitmap_top is distance from baseline to top edge of bitmap
                gx = x_offset + (pos.x_offset / 64.0) + ft_face.glyph.bitmap_left
                gy = y_baseline - (pos.y_offset / 64.0) - ft_face.glyph.bitmap_top
                
                # Create a solid color image for this glyph
                glyph_img = Image.new('RGBA', (bitmap.width, bitmap.rows), color)
                # Apply the mask to the alpha channel
                glyph_img.putalpha(glyph_mask)
                
                # Paste it onto our canvas
                img.alpha_composite(glyph_img, (int(gx), int(gy)))
            
            # Move cursor
            x_offset += pos.x_advance / 64.0
            y_baseline -= pos.y_advance / 64.0
            
        # Trim empty space
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
            
        return img

    except Exception as e:
        logger.error(f"Manual shaping failed: {e}", exc_info=True)
        return None
