from factories.single_clip import generate_mushaf_page_clip, generate_background
from db_ops.crud_mushaf import get_mushaf_page_data
from moviepy.editor import CompositeVideoClip
from config_manager import config_manager
import os
import sys

# Add project root to path for local imports if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def generate_verification_frame(page_number, output_name, border_enabled):
    print(f"Generating verification frame for Page {page_number}, Border Enabled: {border_enabled}...")
    
    # Set override
    config_manager.set_local_override("MUSHAF_BORDER_ENABLED", "True" if border_enabled else "False")
    config_manager.set_local_override("MUSHAF_BORDER_WIDTH_PERCENT", "40")
    
    lines = get_mushaf_page_data(page_number)
    if not lines:
        print(f"No data found for Page {page_number}")
        return

    # Generate only a short clip to save time, and we'll save just one frame
    clip = generate_mushaf_page_clip(lines, page_number=page_number, is_short=False, duration=1.0)
    bg = generate_background("#000000", duration=1.0, is_short=False)
    final = CompositeVideoClip([bg, clip])

    output_path = f"{output_name}.png"
    print(f"Saving frame to {output_path}...")
    final.save_frame(output_path, t=0.5)
    print(f"Done.")

if __name__ == "__main__":
    # Test Border Disabled (Should be no border)
    generate_verification_frame(1, "verify_border_disabled", False)
    
    # Test Border Enabled (Should have border)
    generate_verification_frame(1, "verify_border_enabled", True)

    # Cleanup overrides
    config_manager.clear_local_overrides()
