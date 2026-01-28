from factories.single_clip import generate_mushaf_page_clip
import os
from PIL import Image
import numpy as np

def reproduce():
    import glob
    for f in glob.glob("repro_*.png"):
        os.remove(f)
            
    width, height = 1080, 1920
    top_margin = height * 0.1
    line_height = (height * 0.8) / 15
    y_pos = top_margin
    
    from factories.single_clip import render_mushaf_text_to_image, calculate_centered_y
    font_path_sura = os.path.abspath(os.path.join("QPC_V2_Font.ttf", "QCF_SurahHeader_COLOR-Regular.ttf"))
    font_path_bsml = os.path.abspath(os.path.join("QPC_V2_Font.ttf", "QCF_BSML.TTF"))
    color = (255, 255, 255)
    
    # 1. Surah Name
    font_size_sura = int(width * 0.15)
    text_sura = "ﱅ "
    img_sura = render_mushaf_text_to_image(text_sura, font_path_sura, font_size_sura, color, (width, font_size_sura))
    y_sura = calculate_centered_y(y_pos, line_height, img_sura.shape[0], "surah_name")
    
    # 2. Bismillah
    font_size_bsml = int(line_height * 1.3)
    text_bsml = "\u00F3"
    img_bsml = render_mushaf_text_to_image(text_bsml, font_path_bsml, font_size_bsml, color, (width, font_size_bsml))
    y_bsml = calculate_centered_y(y_pos + line_height, line_height, img_bsml.shape[0], "basmallah")
    
    from moviepy.editor import ImageClip, CompositeVideoClip, ColorClip
    
    t_clip1 = ImageClip(img_sura).set_position(('center', int(y_sura))).set_duration(1.0)
    t_clip2 = ImageClip(img_bsml).set_position(('center', int(y_bsml))).set_duration(1.0)
    bg = ColorClip(size=(width, height), color=(0, 0, 0)).set_duration(1.0)
    
    composite = CompositeVideoClip([bg, t_clip1, t_clip2], size=(width, height))
    frame = composite.get_frame(0)
    
    Image.fromarray(frame).save("repro_clean.png")
    print("Saved repro_clean.png")

if __name__ == "__main__":
    reproduce()

if __name__ == "__main__":
    reproduce()

if __name__ == "__main__":
    reproduce()

if __name__ == "__main__":
    reproduce()
