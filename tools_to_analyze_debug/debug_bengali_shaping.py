from PIL import Image, ImageDraw, ImageFont
from factories.font_utils import resolve_font_path
from factories.shaping_utils import render_shaped_text
import numpy as np

def test_bengali_render():
    # Bengali text: "সমস্ত প্রশংসা আল্লাহর জন্য, যিনি সকল সৃষ্টির পালনকর্তা।"
    text = "সমস্ত প্রশংসা আল্লাহর জন্য, যিনি সকল সৃষ্টির পালনকর্তা।"
    font_path = resolve_font_path("kalpurush.ttf")
    font_size = 40
    
    img = Image.new('RGB', (800, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 1. Render without direction (Broken)
    try:
        font = ImageFont.truetype(font_path, font_size)
        draw.text((10, 50), "Default (Broken): " + text, font=font, fill=(0, 0, 0))
    except Exception as e:
        print(f"Error with default: {e}")
    
    # 2. Render with direction='ltr' (requires libraqm)
    try:
        draw.text((10, 120), "LTR (raqm): " + text, font=font, fill=(0, 0, 0), direction='ltr')
    except Exception as e:
        print(f"Error with direction='ltr' (likely missing libraqm): {e}")

    # 3. Render with Manual Shaping (New Solution)
    try:
        shaped_img = render_shaped_text(text, font_path, font_size, (0, 0, 0))
        if shaped_img:
            img.paste(shaped_img, (10, 190), shaped_img)
            draw.text((10, 190 - 30), "Manual Shaping (Fixed):", font=ImageFont.load_default(), fill=(255, 0, 0))
    except Exception as e:
        print(f"Error with manual shaping: {e}")

    img.save("test_bengali_fixed.png")
    print("Saved test_bengali_fixed.png")

if __name__ == "__main__":
    test_bengali_render()
