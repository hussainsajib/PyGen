import os
import sys
from PIL import Image
import numpy as np

sys.path.append(os.getcwd())

from db_ops.crud_mushaf import get_mushaf_page_data
from factories.single_clip import render_mushaf_text_to_image, calculate_mushaf_font_size

def repro():
    # Setup
    width = 1080
    line_height = (1920 * 0.8) / 15
    font_scale = 0.8
    color = (255, 255, 255) # White text
    
    # 1. Surah 110:3, Line 10 on Page 603
    page_603 = get_mushaf_page_data(603)
    line_110_3 = next(l for l in page_603 if l["line_number"] == 10)
    words_110_3 = line_110_3["words"]
    
    # Current logic in factories/single_clip.py
    text_110_3 = "".join([u'\u200f'+w["text"] for w in reversed(words_110_3)])
    
    font_path_603 = os.path.abspath(os.path.join("QPC_V2_Font.ttf", "p603.ttf"))
    font_size = calculate_mushaf_font_size(width, line_height, "ayah", font_scale)
    
    img_110_3 = render_mushaf_text_to_image(text_110_3, font_path_603, font_size, color, (width, int(line_height)))
    Image.fromarray(img_110_3).save("repro_110_3.png")
    print(f"Saved repro_110_3.png with text: {text_110_3}")

    # 2. Surah 2:5, Line 7 on Page 2
    page_2 = get_mushaf_page_data(2)
    line_2_5 = next(l for l in page_2 if l["line_number"] == 7)
    words_2_5 = line_2_5["words"]
    
    # Current logic in factories/single_clip.py
    text_2_5 = "".join([u'\u200f'+w["text"] for w in reversed(words_2_5)])
    
    font_path_2 = os.path.abspath(os.path.join("QPC_V2_Font.ttf", "p2.ttf"))
    
    img_2_5 = render_mushaf_text_to_image(text_2_5, font_path_2, font_size, color, (width, int(line_height)))
    Image.fromarray(img_2_5).save("repro_2_5.png")
    print(f"Saved repro_2_5.png with text: {text_2_5}")

if __name__ == "__main__":
    repro()
