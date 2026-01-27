from PIL import Image, ImageFont, ImageDraw
import os

def analyze_font(font_path, chars):
    font_size = 200
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        return
    
    print(f"\n--- Analysis of {os.path.basename(font_path)} ---")
    
    img = Image.new('RGBA', (2000, 2000))
    draw = ImageDraw.Draw(img)
    
    results = []
    for i in chars:
        char = chr(i)
        bbox = draw.textbbox((0, 0), char, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w > 0 and h > 0:
            results.append((char, i, w, h))
    
    # Sort by width descending
    results.sort(key=lambda x: x[2], reverse=True)
    
    print(f"Top 10 widest characters in range:")
    for char, i, w, h in results[:10]:
        print(f"U+{i:04X}: W={w}, H={h}")

if __name__ == "__main__":
    # Scan F000 range for QCF_SURA
    chars = range(0xF000, 0xF100)
    analyze_font(os.path.join("QPC_V2_Font.ttf", "QCF_SURA.TTF"), chars)
