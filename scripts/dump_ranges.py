import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = {
    "Color": "QPC_V2_Font.ttf/QCF_SurahHeader_COLOR-Regular.ttf",
    "Sura": "QPC_V2_Font.ttf/QCF_SURA.TTF"
}
OUTPUT_DIR = "surah_tests"

def dump_ranges():
    surah_num = 1 # Test with Al-Fatiha
    
    ranges = [
        ("ASCII_Offset32", chr(surah_num + 32)),
        ("ASCII_Offset64", chr(surah_num + 64)),
        ("PUA_E9xx", chr(0xE900 + surah_num)),
        ("PUA_F3xx", chr(0xF300 + surah_num)),
        ("PresForms_FBxx", chr(0xFB00 + surah_num)),
        ("PUA_F0xx", chr(0xF000 + surah_num)),
        ("Ligature", f"surah{surah_num:03d}"),
        ("Direct_LowByte", chr(surah_num)),
        ("ASCII_Digit", str(surah_num))
    ]
    
    for font_name, font_path in FONT_PATHS.items():
        if not os.path.exists(font_path):
            print(f"Font {font_name} not found at {font_path}")
            continue
        font = ImageFont.truetype(font_path, 100)
        for label, text in ranges:
            img = Image.new('RGBA', (800, 200), (255, 255, 255, 255))
            draw = ImageDraw.Draw(img)
            try:
                draw.text((50, 50), text, font=font, fill=(0,0,0,255))
            except Exception as e:
                print(f"Error drawing {label} with {font_name}: {e}")
                
            filename = f"{font_name}_{label}.png"
            img.save(os.path.join(OUTPUT_DIR, filename))
            # print(f"Saved {filename}")

if __name__ == "__main__":
    dump_ranges()
