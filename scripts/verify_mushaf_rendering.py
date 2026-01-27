from factories.single_clip import generate_mushaf_page_clip
from db_ops.crud_mushaf import get_mushaf_page_data
from moviepy.editor import ColorClip, CompositeVideoClip
import os
import sys

# Add project root to path for local imports if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def generate_verification_video(page_number, output_name):
    print(f"Fetching data for Page {page_number}...")
    lines = get_mushaf_page_data(page_number)
    
    if not lines:
        print(f"No data found for Page {page_number}")
        return

    print(f"Generating clip for Page {page_number} with {len(lines)} lines...")
    # Note: This uses Page font (p{page_number}.ttf) if available in QPC_V2_Font.ttf/
    clip = generate_mushaf_page_clip(lines, page_number=page_number, is_short=False, duration=5.0)

    # Overlay on a dark background to make it visible
    bg = ColorClip(size=clip.size, color=(20, 20, 20)).set_duration(5.0)
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
    bg = ColorClip(size=clip.size, color=(20, 20, 20)).set_duration(5.0)
    final = CompositeVideoClip([bg, clip])
    
    output_path = f"{output_name}.mp4"
    final.write_videofile(output_path, fps=24)
    print(f"Done. Please check {output_path}.")

if __name__ == "__main__":
    # Test with Page 1 (Fatiha) and Page 2 (Baqarah start)
    generate_verification_video(1, "verify_page_1")
    generate_verification_video(2, "verify_page_2")
    generate_verification_video(3, "verify_page_3")
    generate_verification_video(187, "verify_page_187")
    generate_verification_video(591, "verify_page_591")
    generate_verification_video(602, "verify_page_602")
    generate_mock_injection_test("verify_injection")
