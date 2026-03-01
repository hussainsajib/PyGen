from factories.single_clip import render_mushaf_text_to_image, get_resolution
from PIL import Image
import numpy as np
import os
import sys

sys.path.append(os.getcwd())

def test_basmallah_render():
    font_path_bsml = os.path.abspath(os.path.join("QPC_V2_Font.ttf", "QCF_BSML.TTF"))
    print(f"Font Path: {font_path_bsml}, Exists: {os.path.exists(font_path_bsml)}")
    
    text = "﷽"
    font_size = 100
    color = (255, 255, 255)
    size = (500, 200)
    
    img = render_mushaf_text_to_image(text, font_path_bsml, font_size, color, size)
    
    # Check if image is not empty (has non-zero alpha)
    has_content = np.any(img[..., 3] > 0)
    print(f"Rendered Bismillah Content Detected: {has_content}")
    
    if has_content:
        # Save for manual inspection if needed
        Image.fromarray(img).save("debug_basmallah.png")
        print("Saved debug_basmallah.png")
    else:
        print("Render resulted in blank image.")

if __name__ == "__main__":
    test_basmallah_render()
