import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "QPC_V2_Font.ttf/QCF_SurahHeader_COLOR-Regular.ttf"

def scan_full_pua():
    font = ImageFont.truetype(FONT_PATH, 100)
    
    # Render chr(0) to get base size
    img = Image.new('RGBA', (800, 200), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), chr(0), font=font, fill=(0,0,0,255))
    base_arr = np.array(img)
    
    found = []
    # Scan common PUA ranges and Pres Forms
    for code in range(0xE000, 0xF8FF):
        char = chr(code)
        img = Image.new('RGBA', (800, 200), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), char, font=font, fill=(0,0,0,255))
        arr = np.array(img)
        
        if not np.array_equal(arr, base_arr):
            # Check if it's not just a different box?
            # Or if it has significantly more non-white pixels
            mask = arr[..., :3].sum(axis=2) < 700 # darker than light grey
            if mask.sum() > 500: # reasonable glyph size
                found.append(code)
                if len(found) <= 10:
                    print(f"Found candidate at {hex(code)}")
                    
    print(f"Total candidates found: {len(found)}")

if __name__ == "__main__":
    scan_full_pua()
