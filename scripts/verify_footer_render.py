import os
import sys
import numpy as np
from PIL import Image

sys.path.append(os.getcwd())

from factories.mushaf_fast_render import MushafRenderer
from factories.single_clip import render_mushaf_text_to_image
from factories.font_utils import resolve_font_path

def verify_pil_render():
    print("--- Verifying PIL Footer Rendering ---")
    font_path = resolve_font_path("Kalpurush")
    print(f"Using font: {font_path}")
    
    # Render a sample Bengali footer text
    text = "সুরাহ আল-ফাতিহা | আবদুর রহমান আস-সুদাইস"
    img_arr = render_mushaf_text_to_image(
        text=text,
        font_path=font_path,
        font_size=50,
        color="rgb(201, 181, 156)",
        size=(1000, 100)
    )
    
    img = Image.fromarray(img_arr)
    output_path = "debug_footer_pil.png"
    img.save(output_path)
    print(f"Saved PIL specimen to {output_path}")

def verify_fast_renderer():
    print("\n--- Verifying MushafRenderer Footer ---")
    renderer = MushafRenderer(
        page_number=1,
        reciter_name="আবদুর রহমান আস-সুদাইস",
        surah_name="আল-ফাতিহা",
        brand_name="তাকওয়া বাংলা",
        total_duration_ms=5000,
        is_short=False,
        lines=[]
    )
    
    # The MushafRenderer pre-renders the static base including footers
    renderer.prepare_static_base()
    
    # self.static_base is a PIL Image object in MushafRenderer
    output_path = "debug_footer_fast.png"
    renderer.static_base.save(output_path)
    print(f"Saved MushafRenderer specimen to {output_path}")

if __name__ == "__main__":
    try:
        verify_pil_render()
    except Exception as e:
        print(f"PIL Render failed: {e}")
        import traceback
        traceback.print_exc()
        
    try:
        verify_fast_renderer()
    except Exception as e:
        print(f"Fast Renderer failed: {e}")
        import traceback
        traceback.print_exc()
