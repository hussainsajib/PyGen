import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

FONT_PATH = "QPC_V2_Font.ttf/QCF_SurahHeader_COLOR-Regular.ttf"

def debug_font_mapping():
    if not os.path.exists(FONT_PATH):
        print(f"Font not found at {FONT_PATH}")
        return

    try:
        font = ImageFont.truetype(FONT_PATH, 50)
    except Exception as e:
        print(f"Failed to load font: {e}")
        return

    print("Scanning font for visible glyphs...")
    
    # Check ASCII range
    check_range(font, 32, 127, "ASCII")
    
    # Check QCF PUA ranges (common)
    check_range(font, 0xE900, 0xEA00, "PUA E9xx")
    check_range(font, 0xF300, 0xF400, "PUA F3xx")
    
    # Check Arabic Presentation Forms
    check_range(font, 0xFB00, 0xFEFF, "Arabic Pres Forms")
    
    # Check common PUA ranges
    check_range(font, 0xF000, 0xF100, "PUA F0xx")

def check_range(font, start, end, label):
    found = []
    for code in range(start, end):
        char = chr(code)
        img = Image.new('RGBA', (100, 100), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        try:
            draw.text((10, 10), char, font=font, fill=(255,255,255))
            arr = np.array(img)
            # Check alpha channel
            if np.any(arr[..., 3] > 0):
                found.append(code)
        except Exception:
            pass
            
    if found:
        print(f"[{label}] Found {len(found)} glyphs. First 5: {[hex(c) for c in found[:5]]}")
    else:
        print(f"[{label}] No glyphs found.")

if __name__ == "__main__":
    debug_font_mapping()
