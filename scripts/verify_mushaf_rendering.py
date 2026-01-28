from factories.single_clip import generate_mushaf_page_clip, generate_background
from db_ops.crud_mushaf import get_mushaf_page_data
from moviepy.editor import ColorClip, CompositeVideoClip
from config_manager import config_manager
import os
import sys

# Add project root to path for local imports if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def generate_verification_video(page_number, output_name, background_input=None):
    print(f"Fetching data for Page {page_number}...")
    lines = get_mushaf_page_data(page_number)
    
    if not lines:
        print(f"No data found for Page {page_number}")
        return

    print(f"Generating clip for Page {page_number} with {len(lines)} lines...")
    # Note: This uses Page font (p{page_number}.ttf) if available in QPC_V2_Font.ttf/
    clip = generate_mushaf_page_clip(lines, page_number=page_number, is_short=False, duration=5.0)

    # Use generate_background to support color/media
    bg = generate_background(background_input, duration=5.0, is_short=False)
    final = CompositeVideoClip([bg, clip])

    output_path = f"{output_name}.mp4"
    print(f"Writing video to {output_path}...")
    final.write_videofile(output_path, fps=24)
    print(f"Done. Please check {output_path}.")

def generate_mock_injection_test(output_name):
    print("Generating Mock Injection Test with Persistent Visibility...")
    # Create a fake page with an injected header and bismillah
    # They should NOT disappear
    lines = [
        {
            "page_number": 100,
            "line_number": 0,
            "line_type": "surah_name",
            "is_centered": True,
            "surah_number": 100, # Al-Adiyat
            "words": [],
            "start_ms": 0,
            "end_ms": 5000
        },
        {
            "page_number": 100,
            "line_number": 1,
            "line_type": "basmallah",
            "is_centered": True,
            "surah_number": 100,
            "words": [],
            "start_ms": 0,
            "end_ms": 5000
        },
        {
            "page_number": 100,
            "line_number": 2,
            "line_type": "ayah",
            "is_centered": False,
            "surah_number": 100,
            "words": [{"text": "وَالْعَادِيَاتِ ضَبْحًا"}],
            "start_ms": 0,
            "end_ms": 5000
        }
    ]
    
    clip = generate_mushaf_page_clip(lines, page_number=100, is_short=False, duration=5.0)
    bg = generate_background("#1a1a1a", duration=5.0, is_short=False)
    final = CompositeVideoClip([bg, clip])
    
    output_path = f"{output_name}.mp4"
    final.write_videofile(output_path, fps=24)
    print(f"Done. Please check {output_path}.")

if __name__ == "__main__":
    # 1. Test Transparent Mode with a Color
    config_manager.set_local_override("MUSHAF_PAGE_BACKGROUND_MODE", "Transparent")
    generate_verification_video(1, "verify_bg_transparent", background_input="#2c3e50")
    
    # 2. Test Semi-Transparent Mode with a Color
    config_manager.set_local_override("MUSHAF_PAGE_BACKGROUND_MODE", "Semi-Transparent")
    config_manager.set_local_override("MUSHAF_PAGE_COLOR", "#FFFFFF") # White semi-transparent
    generate_verification_video(2, "verify_bg_semi", background_input="#1a1a1a")
    
    # 3. Test Solid Mode (Default)
    config_manager.set_local_override("MUSHAF_PAGE_BACKGROUND_MODE", "Solid")
        config_manager.set_local_override("MUSHAF_PAGE_COLOR", "#FFFDF5")
    generate_verification_video(3, "verify_bg_solid", background_input="#000000")

    # Cleanup overrides
    config_manager.clear_local_overrides()
    generate_mock_injection_test("verify_injection")
