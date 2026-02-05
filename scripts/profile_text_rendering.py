import os
import time
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from factories.single_clip import render_mushaf_text_to_image

def profile_rendering():
    print("--- Profiling render_mushaf_text_to_image ---")
    pages = [1, 100, 604]
    font_sizes = [60, 100, 150]
    sample_text = "ﱁﱂﱃﱄﱅ" # Some sample glyphs
    color = "rgb(201, 181, 156)"
    
    for page in pages:
        font_path = os.path.abspath(os.path.join("QPC_V2_Font.ttf", f"p{page}.ttf"))
        if not os.path.exists(font_path):
            print(f"Font for page {page} not found, skipping.")
            continue
            
        print(f"\nProfiling Page {page} Font:")
        for size in font_sizes:
            # Warmup
            render_mushaf_text_to_image(sample_text, font_path, size, color, (1080, size))
            
            iterations = 10
            start_time = time.time()
            for _ in range(iterations):
                render_mushaf_text_to_image(sample_text, font_path, size, color, (1080, size))
            end_time = time.time()
            
            avg_time = (end_time - start_time) / iterations
            print(f"  Font Size {size}: {avg_time:.4f}s per render")

if __name__ == "__main__":
    profile_rendering()
