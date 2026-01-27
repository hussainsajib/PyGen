from PIL import Image, ImageFont, ImageDraw
import os

def analyze_font_full(font_path):
    font_size = 200
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        return
    
    print(f"\n--- Full Analysis of {os.path.basename(font_path)} ---")
    
    results = []
    for i in range(32, 0xFFFF):
        char = chr(i)
        bbox = font.getbbox(char)
        if bbox:
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            if w > 0 and h > 0:
                results.append((i, w, h))
    
    # Sort by width
    results.sort(key=lambda x: x[1], reverse=True)
    
    print(f"Widest characters:")
    for i, w, h in results[:50]:
        print(f"U+{i:04X}: W={w}, H={h}")

if __name__ == "__main__":
    analyze_font_full(os.path.join("QPC_V2_Font.ttf", "QCF_SurahHeader_COLOR-Regular.ttf"))

