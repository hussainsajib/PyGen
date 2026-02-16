from factories.mushaf_fast_render import MushafRenderer
from PIL import Image
import os

def repro_juz_footer():
    # Setup dummy data for Juz 1
    juz_number = 1
    reciter_name = "মিশারি আল-আফাসি"
    # Localized juz name as it would be passed by generate_mushaf_fast or generate_juz_video
    juz_display_name = "পারা ১"
    brand_name = "তাকওয়া বাংলা"
    
    # Create renderer for page 1
    renderer = MushafRenderer(
        page_number=1,
        is_short=False,
        lines=[], # We just want to see the overlays
        font_scale=0.8,
        background_input=None,
        reciter_name=reciter_name,
        surah_name=juz_display_name,
        brand_name=brand_name,
        total_duration_ms=5000
    )
    
    # Pre-render the static base (this calls _draw_overlays)
    renderer.prepare_static_base()
    
    # Save the result
    output_path = "repro_juz_footer_bengali.png"
    renderer.static_base.save(output_path)
    print(f"Juz footer frame saved to {output_path}")

if __name__ == "__main__":
    repro_juz_footer()
