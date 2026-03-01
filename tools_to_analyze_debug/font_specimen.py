from PIL import Image, ImageFont, ImageDraw
import os

def create_specimen(font_path, output_path, chars):
    font_size = 100
    img_w = 2000
    img_h = 1000
    img = Image.new('RGBA', (img_w, img_h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        print(f"Failed to load {font_path}")
        return

    x, y = 10, 10
    for char in chars:
        txt = f"{char}"
        bbox = draw.textbbox((x, y), txt, font=font)
        draw.text((x, y), txt, font=font, fill=(0, 0, 0, 255))
        draw.text((x, y + 110), f"U+{ord(char):04X}", font=ImageFont.load_default(), fill=(255, 0, 0, 255))
        x += (bbox[2] - bbox[0]) + 50
        if x > img_w - 200:
            x = 10
            y += 200
        if y > img_h - 200:
            break
            
    img.save(output_path)
    print(f"Saved {output_path}")

if __name__ == "__main__":
    bsml_path = os.path.join("QPC_V2_Font.ttf", "QCF_BSML.TTF")
    # Try common ASCII and some PUAs
    chars = [chr(i) for i in range(33, 127)] + [chr(i) for i in range(0xF000, 0xF020)] + ["﷽"]
    create_specimen(bsml_path, "specimen_bsml.png", chars)
    
    sura_path = os.path.join("QPC_V2_Font.ttf", "QCF_SurahHeader_COLOR-Regular.ttf")
    # Try the first few surahs from my map
    sura_chars = [chr(0xFC45), chr(0xFC46), chr(0xFC47)] + [chr(i) for i in range(65, 90)]
    create_specimen(sura_path, "specimen_sura.png", sura_chars)
