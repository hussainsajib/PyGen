import os
import time
import sys
from PIL import ImageFont

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from factories.single_clip import render_mushaf_text_to_image

def benchmark_caching():
    print("--- Benchmarking Font Caching ---")
    page = 1
    font_path = os.path.abspath(os.path.join("QPC_V2_Font.ttf", f"p{page}.ttf"))
    sample_text = "ﱁﱂﱃﱄﱅ"
    font_size = 100
    color = "rgb(201, 181, 156)"
    
    # Test Uncached (Simulation if cache not yet implemented)
    iterations = 100
    start_time = time.time()
    for _ in range(iterations):
        # Current implementation inside factories/single_clip.py loads font every time
        render_mushaf_text_to_image(sample_text, font_path, font_size, color, (1080, font_size))
    uncached_total = time.time() - start_time
    print(f"Total time (Current/Uncached): {uncached_total:.4f}s ({uncached_total/iterations:.4f}s per render)")

if __name__ == "__main__":
    benchmark_caching()
