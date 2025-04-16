from factories.video import get_resolution
from processes.backgrounds import crop_image

def edit_image(background_image_url: str, is_short: bool):
    file_name = background_image_url.split("/")[-1]
    output_path = f"background/c_{file_name}"
    target_resolution = get_resolution(is_short)
    return crop_image(background_image_url, output_path, target_resolution[0], target_resolution[1])
