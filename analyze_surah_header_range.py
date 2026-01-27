from PIL import Image, ImageFont, ImageDraw
import os
import sys

def analyze_range(font_name, start, end):
    font_path = os.path.join("QPC_V2_Font.ttf", font_name)
    font_size = 200
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        print(f"Failed to load {font_path}")
        return
    
    print(f"\n--- Range Analysis of {font_name} ({hex(start)}-{hex(end)}) ---")
    
    results = []
    for i in range(start, end + 1):
        char = chr(i)
        bbox = font.getbbox(char)
        if bbox:
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            if w > 0 and h > 0:
                results.append((i, w, h))
    
    for i, w, h in results:
        print(f"U+{i:04X}: W={w}, H={h}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python script.py font_name start_hex end_hex")
    else:
        analyze_range(sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16))