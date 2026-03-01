from PIL import Image, ImageFont, ImageDraw
import os

def render_char(font_path, char_code, output_path):
    font_size = 200
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        return
    
    img = Image.new('RGBA', (1000, 400), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    char = chr(char_code)
    bbox = draw.textbbox((0, 0), char, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    
    x = (1000 - w) // 2
    y = (400 - h) // 2
    draw.text((x, y), char, font=font, fill=(0, 0, 0, 255))
    
    img.save(output_path)
    print(f"Saved {output_path} (W={w}, H={h})")

if __name__ == "__main__":
    font_path = os.path.join("QPC_V2_Font.ttf", "QCF_SurahHeader_COLOR-Regular.ttf")
    render_char(font_path, 0xFC45, "surah_1_header.png")
    render_char(font_path, 0x0073, "char_s_header.png")
    
    sura_font = os.path.join("QPC_V2_Font.ttf", "QCF_SURA.TTF")
    render_char(sura_font, 0xE000, "surah_1_name.png")
