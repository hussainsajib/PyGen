from PIL import Image, ImageFont, ImageDraw
import numpy as np
import os

def analyze_font_comprehensive(font_path):
    font_size = 200
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        return
    
    print(f"\n--- Analysis of {os.path.basename(font_path)} ---")
    
    img = Image.new('RGBA', (2000, 2000))
    draw = ImageDraw.Draw(img)
    
    results = []
    # Scan a wide range of characters
    for i in range(32, 0xFFFF):
        char = chr(i)
        bbox = draw.textbbox((0, 0), char, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w > 0 and h > 0:
            results.append((char, i, w, h))
    
    # Sort by width descending
    results.sort(key=lambda x: x[2], reverse=True)
    print("Top 10 widest characters:")
    for char, i, w, h in results[:10]:
        print(f"U+{i:04X}: W={w}, H={h}")
        
    # Sort by height descending
    results.sort(key=lambda x: x[3], reverse=True)
    print("\nTop 10 tallest characters:")
    for char, i, w, h in results[:10]:
        print(f"U+{i:04X}: W={w}, H={h}")

if __name__ == "__main__":
    analyze_font_comprehensive(os.path.join("QPC_V2_Font.ttf", "QCF_BSML.TTF"))
    analyze_font_comprehensive(os.path.join("QPC_V2_Font.ttf", "QCF_SurahHeader_COLOR-Regular.ttf"))
