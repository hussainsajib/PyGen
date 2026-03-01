from moviepy.editor import TextClip
from factories.font_utils import resolve_font_path
from PIL import Image
import os

def test_formats():
    text = "সমস্ত প্রশংসা আল্লাহর জন্য" # Bengali: "All praise is for Allah"
    font_path = resolve_font_path("kalpurush.ttf")
    print(f"Base font path: {font_path}")
    
    formats = [
        font_path,
        font_path.replace("\\", "/"),
        "@" + font_path.replace("\\", "/"),
        "Kalpurush" # Try by name if registered
    ]
    
    for i, fmt in enumerate(formats):
        print(f"\nTesting format {i}: {fmt}")
        try:
            clip = TextClip(text, font=fmt, fontsize=40, color='white', bg_color='black')
            clip.save_frame(f"debug_format_{i}.png")
            print(f"Success! Saved debug_format_{i}.png")
        except Exception as e:
            print(f"Failed: {e}")

if __name__ == "__main__":
    test_formats()
