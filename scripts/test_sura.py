import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "QPC_V2_Font.ttf/QCF_SURA.TTF"
OUTPUT_DIR = "surah_tests"

def test_sura_ascii():
    font = ImageFont.truetype(FONT_PATH, 100)
    for surah_num in range(1, 10):
        char = chr(surah_num + 32)
        img = Image.new('RGBA', (800, 200), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), char, font=font, fill=(0,0,0,255))
        
        filename = f"Sura_Offset32_{surah_num}.png"
        img.save(os.path.join(OUTPUT_DIR, filename))
        print(f"Saved {filename}")

if __name__ == "__main__":
    test_sura_ascii()
