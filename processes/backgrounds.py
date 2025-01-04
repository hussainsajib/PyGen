from PIL import Image

def crop_image(input_path, output_path, target_width, target_height):
    """
    Crops an image to the center with the specified resolution.

    Args:
        input_path (str): Path to the input image.
        output_path (str): Path to save the cropped image.
        target_width (int): Desired width of the cropped image.
        target_height (int): Desired height of the cropped image.
    """
    with Image.open(input_path) as img:
        original_width, original_height = img.size
        target_aspect_ratio = target_width / target_height
        
        # Resize the image if smaller than the target dimensions
        #if original_width < target_width or original_height < target_height:
        original_aspect_ratio = original_width / original_height
        # Determine new dimensions to maintain aspect ratio
        if original_aspect_ratio > target_aspect_ratio:
            new_height = target_height
            new_width = int(new_height * original_aspect_ratio)
        else:
            new_width = target_width
            new_height = int(new_width / original_aspect_ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
        # Update resized dimensions
        resized_width, resized_height = img.size
        
        # Calculate cropping box to center the crop
        left = (resized_width - target_width) // 2
        top = (resized_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height

        try:
            # Crop the image
            cropped_img = img.crop((left, top, right, bottom))
            # Save the cropped image
            cropped_img.save(output_path)
        except Exception as e:
            print(str(e))
        else:
            return output_path
        