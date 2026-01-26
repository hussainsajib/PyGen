import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "QPC_V2_Font.ttf/QCF_SurahHeader_COLOR-Regular.ttf"
OUTPUT_DIR = "surah_tests"

def test_mappings():
    font = ImageFont.truetype(FONT_PATH, 100)
    
    # Try the ranges found in glyph names
    mappings = [
        ("FB51", 0xFB51),
        ("FC45", 0xFC45)
    ]
    
    for label, base_code in mappings:
        for i in range(1, 6):
            code = base_code + (i - 1)
            char = chr(code)
            img = Image.new('RGBA', (800, 200), (255, 255, 255, 255))
            draw = ImageDraw.Draw(img)
            draw.text((50, 50), char, font=font, fill=(0,0,0,255))
            
            filename = f"Map_{label}_Surah_{i}.png"
            img.save(os.path.join(OUTPUT_DIR, filename))
            print(f"Saved {filename}")

if __name__ == "__main__":
    test_mappings()
