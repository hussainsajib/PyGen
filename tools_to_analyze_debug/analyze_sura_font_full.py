from PIL import Image, ImageFont, ImageDraw
import os
import sys

def analyze_font_full(font_path):
    font_size = 200
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        return
    
    print(f"\n--- Full Analysis of {os.path.basename(font_path)} ---")
    
    results = []
    # Scan a wider range
    for i in range(32, 0xFFFF):
        char = chr(i)
        bbox = font.getbbox(char)
        if bbox:
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            if w > 0 and h > 0:
                results.append((i, w, h))
    
    print(f"Found {len(results)} valid characters.")
    # Sort by code point
    results.sort()
    
    for i, w, h in results[:20]:
        print(f"U+{i:04X}: W={w}, H={h}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <font_name.ttf>")
    else:
        font_name = sys.argv[1]
        analyze_font_full(os.path.join("QPC_V2_Font.ttf", font_name))