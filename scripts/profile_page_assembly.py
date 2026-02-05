import os
import time
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from factories.single_clip import generate_mushaf_page_clip

def profile_page_assembly():
    print("--- Profiling generate_mushaf_page_clip (Assembly) ---")
    
    # 15 lines - typical max for a page
    lines = []
    for i in range(15):
        lines.append({
            "line_number": i + 1,
            "line_type": "ayah",
            "words": [{"text": "ﱁﱂﱃ"}],
            "start_ms": i * 1000,
            "end_ms": (i + 1) * 1000
        })
        
    duration = 15.0
    page_number = 1
    
    # Warmup
    generate_mushaf_page_clip(lines, page_number, is_short=False, duration=duration)
    
    iterations = 5
    start_time = time.time()
    for _ in range(iterations):
        generate_mushaf_page_clip(lines, page_number, is_short=False, duration=duration)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / iterations
    print(f"\nAverage generate_mushaf_page_clip time (15 lines): {avg_time:.4f}s")

if __name__ == "__main__":
    profile_page_assembly()
