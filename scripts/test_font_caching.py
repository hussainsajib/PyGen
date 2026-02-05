import os
import time
import sys
from PIL import ImageFont

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from factories.single_clip import render_mushaf_text_to_image

def test_font_caching():
    print("--- Testing Font Caching Impact ---")
    page = 1
    font_path = os.path.abspath(os.path.join("QPC_V2_Font.ttf", f"p{page}.ttf"))
    sample_text = "ﱁﱂﱃﱄﱅ"
    font_size = 100
    color = "rgb(201, 181, 156)"
    
    # 1. Without Caching (Current implementation, but we'll mock it by calling ImageFont inside the loop if we were editing it)
    # Actually factories/single_clip.py already calls ImageFont.truetype inside the function.
    
    iterations = 50
    start_time = time.time()
    for _ in range(iterations):
        render_mushaf_text_to_image(sample_text, font_path, font_size, color, (1080, font_size))
    uncached_time = (time.time() - start_time) / iterations
    print(f"Average time without explicit caching: {uncached_time:.4f}s")
    
    # 2. Manual Caching Simulation
    # We can't easily change factories/single_clip.py for this test without permanent edits,
    # but we can profile ImageFont.truetype itself.
    
    start_time = time.time()
    for _ in range(iterations):
        font = ImageFont.truetype(font_path, font_size)
    font_load_time = (time.time() - start_time) / iterations
    print(f"Average ImageFont.truetype time: {font_load_time:.4f}s")
    
    print(f"Font loading represents ~{(font_load_time / uncached_time) * 100:.1f}% of render time.")

if __name__ == "__main__":
    test_font_caching()
