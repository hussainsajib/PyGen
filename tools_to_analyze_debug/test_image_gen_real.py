import os
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

from factories.image_generator import ImageGenerator
from db_ops.crud_mushaf import get_page_for_verse
from db_ops.crud_wbw import get_wbw_text_for_ayah
from db_ops.crud_text import get_full_translation_for_ayah

def test_real_generation():
    surah = 1
    ayah = 1
    
    # 1. Get real data
    page_number = get_page_for_verse(surah, ayah)
    db_wbw_path = "databases/text/word_by_word_qpc-v2.db"
    words = get_wbw_text_for_ayah(db_wbw_path, surah, ayah)
    
    translation = get_full_translation_for_ayah(surah, ayah, language="bengali")
    
    print(f"Data: Page={page_number}, Words={words}, Translation={translation}")
    
    # 2. Generate Image
    gen = ImageGenerator()
    
    # Use an existing background from the listing
    bg_path = "background/dawn.jpg"
    if os.path.exists(bg_path):
        gen.set_background(bg_path, dim_opacity=0.4)
    else:
        print(f"Warning: {bg_path} not found, using white background")
    
    # Render layers
    y = 200
    h = gen.render_arabic_ayah(words, page_number, font_size=80, y_pos=y)
    
    y = 500
    h = gen.render_bangla_translation(translation, font_size=45, y_pos=y)
    
    y = 650
    surah_name_bangla = "সূরা ফাতিহা"
    gen.render_metadata(surah_name_bangla, ayah, font_size=35, y_pos=y)
    
    gen.render_branding()
    
    output_path = "test_post.png"
    gen.save(output_path)
    print(f"Successfully generated test image: {output_path}")

if __name__ == "__main__":
    test_real_generation()
