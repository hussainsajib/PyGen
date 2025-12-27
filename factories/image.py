import os
from factories.video import get_resolution
from processes.backgrounds import crop_image

def edit_image(background_image_path: str, is_short: bool):
    file_name = os.path.basename(background_image_path)
    background_dir = "background"
    if not os.path.exists(background_dir):
        os.makedirs(background_dir)
        
    output_path = os.path.join(background_dir, f"c_{file_name}")
    target_resolution = get_resolution(is_short)
    return crop_image(background_image_path, output_path, target_resolution[0], target_resolution[1])
