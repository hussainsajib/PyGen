from factories.single_clip import generate_mushaf_page_clip
import os
from PIL import Image
import numpy as np

def reproduce():
    # Mock lines for Surah 1
    lines = [
        {"line_type": "surah_name", "surah_number": 1},
        {"line_type": "basmallah", "words": []},
        {"line_type": "ayah", "words": [{"text": "A"}]}, # Dummy ayah line
    ]
    
    # Generate for short video (portrait)
    clip = generate_mushaf_page_clip(lines, page_number=1, is_short=True, duration=1.0)
    
    # Save a frame
    frame = clip.get_frame(0)
    Image.fromarray(frame).save("repro_surah_1.png")
    print("Saved repro_surah_1.png")

    # Mock lines for another surah to see consistent misalignment
    lines_2 = [
        {"line_type": "surah_name", "surah_number": 114},
        {"line_type": "basmallah", "words": []},
        {"line_type": "ayah", "words": [{"text": "B"}]},
    ]
    clip_2 = generate_mushaf_page_clip(lines_2, page_number=604, is_short=True, duration=1.0)
    frame_2 = clip_2.get_frame(0)
    Image.fromarray(frame_2).save("repro_surah_114.png")
    print("Saved repro_surah_114.png")

if __name__ == "__main__":
    reproduce()
