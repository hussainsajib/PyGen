import os
import time
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from factories.single_clip import generate_mushaf_page_clip

def test_params():
    print("--- Testing write_videofile Parameters ---")
    
    lines = [{
        "line_number": 1,
        "line_type": "ayah",
        "words": [{"text": "ﱁﱂﱃ"}],
        "start_ms": 0,
        "end_ms": 5000
    }]
    duration = 5.0
    page_number = 1
    clip = generate_mushaf_page_clip(lines, page_number, is_short=False, duration=duration)
    output_path = "param_test.mp4"
    
    scenarios = [
        {"threads": 1, "preset": "ultrafast"},
        {"threads": 4, "preset": "ultrafast"},
        {"threads": 12, "preset": "ultrafast"},
        {"threads": 12, "preset": "medium"},
    ]
    
    for s in scenarios:
        print(f"\nTesting: threads={s['threads']}, preset={s['preset']}")
        start_time = time.time()
        clip.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=s['threads'],
            preset=s['preset'],
            logger=None
        )
        elapsed = time.time() - start_time
        print(f"  Time: {elapsed:.2f}s")
    
    if os.path.exists(output_path):
        os.remove(output_path)

if __name__ == "__main__":
    test_params()
