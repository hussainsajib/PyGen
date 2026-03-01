from moviepy.editor import TextClip
from factories.font_utils import resolve_font_path
from PIL import Image
import numpy as np

def test_textclip():
    text = 'সমস্ত প্রশংসা আল্লাহর জন্য, যিনি সকল সৃষ্টির পালনকর্তা।'
    font = resolve_font_path("kalpurush.ttf")
    print(f"Using font: {font}")
    
    try:
        clip = TextClip(
            text, 
            font=font, 
            fontsize=30, 
            color='white', 
            method='caption', 
            size=(800, None)
        )
        frame = clip.get_frame(0)
        img = Image.fromarray(frame)
        print(f"Image size: {img.size}")
        img.save("debug_textclip.png")
        print("Saved debug_textclip.png")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_textclip()
