import os
import sys
import numpy as np
from PIL import Image

# Add project root to path
sys.path.append(os.getcwd())

from factories.mushaf_fast_render import MushafRenderer
from db_ops.crud_mushaf import get_mushaf_page_data

def reproduce():
    print("Reproducing highlight issue with real data...")
    
    # Get real data for page 1
    page_num = 1
    lines = get_mushaf_page_data(page_num)
    print(f"Found {len(lines)} lines on page {page_num}")
    for i, l in enumerate(lines):
        word_text = "".join([w['text'] for w in l['words']])
        print(f"Line {i}: Type={l['line_type']}, Surah={l['surah_number']}, Words={len(l['words'])}, Text='{word_text}'")
    
    # Manually add some timestamps for testing highlights
    # Let's highlight the first Ayah line (usually index 2 after header and basmallah)
    # Page 1 of Mushaf is Surah 1 (Al-Fatiha)
    # Line 0: surah_name (suppressed in crud if Surah 1, but let's check)
    # Line 1: basmallah (suppressed in crud if Surah 1)
    # Wait, Surah 1 basmallah is Ayah 1.
    
    found_ayah = False
    for i, line in enumerate(lines):
        if line["line_type"] == "ayah":
            print(f"Highlighting line {i}")
            line["start_ms"] = 1000
            line["end_ms"] = 5000
            found_ayah = True
            break
    
    if not found_ayah:
        print("WARNING: No ayah lines found to highlight!")
    
    renderer = MushafRenderer(
        page_number=page_num,
        is_short=True,
        lines=lines,
        font_scale=0.8,
        background_input="#000000", # Black background
        reciter_name="Mishari Rashid",
        surah_name="Al-Fatiha",
        brand_name="Taqwa",
        total_duration_ms=10000
    )
    print(f"Font path: {renderer.font_paths['page']}")
    print(f"Font exists: {os.path.exists(renderer.font_paths['page'])}")
    
    # Pre-render static base
    renderer.prepare_static_base()
    renderer.static_base.save("debug_highlight_static.png")
    print("Saved debug_highlight_static.png")
    
    # 1. Base frame (no highlight at 0.5s)
    frame_base = renderer.get_frame_at(0.5)
    Image.fromarray(frame_base).save("debug_highlight_base.png")
    print("Saved debug_highlight_base.png")
    
    # 2. Highlight frame (at 2.0s)
    frame_high = renderer.get_frame_at(2.0)
    Image.fromarray(frame_high).save("debug_highlight_active.png")
    print("Saved debug_highlight_active.png")
    
    print("Reproduction complete. Please check the PNG files.")

if __name__ == "__main__":
    reproduce()
