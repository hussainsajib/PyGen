from factories.single_clip import render_mushaf_text_to_image
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import os
import sys

sys.path.append(os.getcwd())

def scan_font():
    font_path = os.path.abspath(os.path.join("QPC_V2_Font.ttf", "QCF_BSML.TTF"))
    font_size = 50
    size = (200, 100)
    color = (255, 255, 255)
    
    # Try common Bismillah chars
    candidates = [
        "﷽", # U+FDFD
        "بسم الله الرحمن الرحيم",
        chr(0xF000), # PUA start
        "A", "a", "1"
    ]
    
    print(f"Scanning {font_path}...")
    
    for text in candidates:
        try:
            img = render_mushaf_text_to_image(text, font_path, font_size, color, size)
            
            # Get bounding box manually from alpha channel
            alpha = img[..., 3]
            coords = np.argwhere(alpha > 0)
            if coords.size > 0:
                y_min, x_min = coords.min(axis=0)
                y_max, x_max = coords.max(axis=0)
                w = x_max - x_min
                h = y_max - y_min
                print(f"Text: {text!r} (len {len(text)}) -> Content Found! W: {w}, H: {h}")
            else:
                print(f"Text: {text!r} -> Blank")
        except Exception as e:
            print(f"Text: {text!r} -> Error: {e}")

if __name__ == "__main__":
    scan_font()
