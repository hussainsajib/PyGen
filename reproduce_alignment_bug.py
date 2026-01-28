from factories.single_clip import generate_mushaf_page_clip
import os
from PIL import Image
import numpy as np
import glob

def reproduce():
    # Remove old files
    for f in glob.glob("repro_final_*.png"):
        os.remove(f)
    
    # Surah 1 (Fatiha) Page 1
    lines_1 = [
        {"line_type": "surah_name", "surah_number": 1},
        {"line_type": "basmallah", "words": []},
        {"line_type": "ayah", "words": [{"text": "الحمد لله رب العالمين"}]},
    ]
    
    print("Generating Surah 1 frame...")
    clip_1 = generate_mushaf_page_clip(lines_1, page_number=1, is_short=True, duration=1.0)
    frame_1 = clip_1.get_frame(0)
    Image.fromarray(frame_1).save("repro_final_surah_1.png")
    print("Saved repro_final_surah_1.png")

    # Surah 2 (Baqarah) Page 2
    # Surah 2 starts with a header on page 2
    lines_2 = [
        {"line_type": "surah_name", "surah_number": 2},
        {"line_type": "basmallah", "words": []},
        {"line_type": "ayah", "words": [{"text": "الم"}]},
    ]
    
    print("Generating Surah 2 frame...")
    clip_2 = generate_mushaf_page_clip(lines_2, page_number=2, is_short=True, duration=1.0)
    frame_2 = clip_2.get_frame(0)
    Image.fromarray(frame_2).save("repro_final_surah_2.png")
    print("Saved repro_final_surah_2.png")

if __name__ == "__main__":
    reproduce()