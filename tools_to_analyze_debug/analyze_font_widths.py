from PIL import Image, ImageFont, ImageDraw
import os

def analyze_font(font_path, chars):
    font_size = 200
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        return
    
    img = Image.new('RGBA', (2000, 2000))
    draw = ImageDraw.Draw(img)
    
    results = []
    for char in chars:
        bbox = draw.textbbox((0, 0), char, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        results.append((char, w, h))
    
    # Sort by width descending
    results.sort(key=lambda x: x[1], reverse=True)
    
    print(f"Top 10 widest characters in {os.path.basename(font_path)}:")
    for char, w, h in results[:10]:
        print(f"Char: {char!r} (U+{ord(char):04X}), W: {w}, H: {h}")

if __name__ == "__main__":
    chars = [chr(i) for i in range(32, 255)] + [chr(i) for i in range(0xF000, 0xFDFF)]
    
    for font_name in ["QCF_BSML.TTF", "QCF_SURA.TTF", "QCF_SurahHeader_COLOR-Regular.ttf"]:
        path = os.path.join("QPC_V2_Font.ttf", font_name)
        if os.path.exists(path):
            analyze_font(path, chars)