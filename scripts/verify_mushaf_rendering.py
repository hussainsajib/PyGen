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

if __name__ == "__main__":
    # Test with Page 1 (Fatiha) and Page 2 (Baqarah start)
    generate_verification_video(1, "verify_page_1")
    generate_verification_video(2, "verify_page_2")
