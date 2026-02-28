from factories.video import get_resolution
from factories.image import edit_image
from moviepy.editor import ImageClip, ColorClip, TextClip, CompositeVideoClip, VideoFileClip, vfx
from moviepy.video.fx.resize import resize
from convert_numbers import english_to_arabic as e2a
from bangla import convert_english_digit_to_bangla_digit as e2b
from processes.video_configs import BACKGROUND_OPACITY, BACKGROUND_RGB, COMMON, FOOTER_CONFIG, SHORT, LONG, FONT_COLOR
from config_manager import config_manager
from factories.font_utils import resolve_font_path
from factories.mushaf_utils import assemble_mushaf_line_text
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import json

from moviepy.config import get_setting

# Load ligature data for Mushaf headers
LIGATURE_DATA = {}
try:
    ligature_path = os.path.abspath(os.path.join("databases", "text", "ligatures.json"))
    if os.path.exists(ligature_path):
        with open(ligature_path, "r", encoding="utf-8") as f:
            LIGATURE_DATA = json.load(f)
except Exception as e:
    print(f"[ERROR] Failed to load ligatures.json: {e}")

# Global font cache to avoid redundant I/O
FONT_CACHE = {}

def get_font_path(font_name: str) -> str:
    """Robustly resolves a font path using shared utility."""
    return resolve_font_path(font_name)
def render_mushaf_text_to_image(text: str, font_path: str, font_size: int, color: str, size: tuple):
    """
    Renders Arabic Mushaf text to a numpy array (image) using Pillow.
    Automatically trims empty space around the rendered text.
    """
    # Create a large enough canvas to avoid initial clipping
    canvas_w = max(size[0], font_size * 10)
    canvas_h = max(size[1], font_size * 2)
    img = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cache_key = f"{font_path}_{font_size}"
    if cache_key in FONT_CACHE:
        font = FONT_CACHE[cache_key]
    else:
        try:
            font = ImageFont.truetype(font_path, font_size)
            FONT_CACHE[cache_key] = font
        except Exception as e:
            print(f"DEBUG: PIL failed to load font {font_path}: {e}")
            font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Draw centered on our temporary large canvas
    x = (canvas_w - text_width) // 2
    y = (canvas_h - text_height) // 2
    draw.text((x, y), text, font=font, fill=color)
    
    # Trim empty space
    img_arr = np.array(img)
    alpha = img_arr[..., 3]
    coords = np.argwhere(alpha > 0)
    if coords.size > 0:
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
        img_arr = img_arr[y_min:y_max+1, x_min:x_max+1]
    else:
        # Return a 1x1 transparent pixel if blank
        img_arr = np.zeros((1, 1, 4), dtype=np.uint8)
        
    return img_arr

def get_pil_background(background_input: str, resolution: tuple):
    """
    Returns a PIL Image for the background.
    If it's a video, returns the first frame (simplification for flattening).
    """
    target_bg = background_input or config_manager.get("ACTIVE_BACKGROUND")
    width, height = resolution
    
    if not target_bg or target_bg.startswith('#'):
        color = hex_to_rgb(target_bg) if target_bg else BACKGROUND_RGB
        # Add opacity to background color
        rgba_color = color + (int(BACKGROUND_OPACITY * 255),)
        return Image.new('RGBA', resolution, rgba_color)
        
    if target_bg.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
        # For video backgrounds, we can't easily flatten them into a static image
        # without losing the animation. 
        # Requirement check: "The global background (image or video frame)" should be flattened.
        # This implies we take a frame.
        import cv2
        cap = cv2.VideoCapture(target_bg)
        ret, frame = cap.read()
        cap.release()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(frame)
        else:
            return Image.new('RGBA', resolution, BACKGROUND_RGB + (255,))
    else:
        if not target_bg or not os.path.isfile(target_bg):
            # Fallback if file missing or is a directory
            return Image.new('RGBA', resolution, BACKGROUND_RGB + (255,))
        img = Image.open(target_bg).convert('RGBA')
        
    # Resize and crop to fill
    img_aspect = img.width / img.height
    target_aspect = width / height
    
    if img_aspect > target_aspect:
        new_h = height
        new_w = int(new_h * img_aspect)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - width) // 2
        img = img.crop((left, 0, left + width, height))
    else:
        new_w = width
        new_h = int(new_w / img_aspect)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        top = (new_h - height) // 2
        img = img.crop((0, top, width, top + height))
        
    # Apply global background opacity
    if BACKGROUND_OPACITY < 1.0:
        alpha = img.getchannel('A')
        alpha = alpha.point(lambda p: int(p * BACKGROUND_OPACITY))
        img.putalpha(alpha)
        
    return img

def draw_mushaf_border_onto(img: Image.Image, usable_height: int, bg_mode: str, bg_color: str, bg_opacity: int):
    """Draws the Mushaf border directly onto the PIL image."""
    width, height = img.size
    draw = ImageDraw.Draw(img)
    
    border_enabled = config_manager.get("MUSHAF_BORDER_ENABLED", "False") == "True"
    if not border_enabled:
        return img
        
    try:
        border_width_percent = int(config_manager.get("MUSHAF_BORDER_WIDTH_PERCENT", "40"))
    except (ValueError, TypeError):
        border_width_percent = 40
        
    border_w = int(width * (border_width_percent / 100))
    border_h = int(usable_height + 60)
    border_color = (212, 197, 161) # Authentic Gold/Bronze
    border_thickness = 8
    border_radius = 25
    
    # Border Box coordinates (centered)
    x0 = (width - border_w) // 2
    y0 = (height - border_h) // 2
    x1 = x0 + border_w
    y1 = y0 + border_h
    
    # 1. Background inside border
    opacity = 255
    if bg_mode == "Transparent": opacity = 0
    elif bg_mode in ["Semi-Transparent", "Semi"]: opacity = bg_opacity
    
    if opacity > 0:
        fill_rgb = hex_to_rgb(bg_color)
        fill_rgba = fill_rgb + (opacity,)
        # Create a temp image for the internal box to handle transparency correctly with alpha blending
        overlay = Image.new('RGBA', img.size, (0,0,0,0))
        d_overlay = ImageDraw.Draw(overlay)
        d_overlay.rounded_rectangle([x0, y0, x1, y1], radius=border_radius, fill=fill_rgba)
        img.alpha_composite(overlay)
        
    # 2. Draw Borders
    draw.rounded_rectangle([x0, y0, x1, y1], radius=border_radius, outline=border_color, width=border_thickness)
    
    inset = border_thickness + 6
    draw.rounded_rectangle([x0 + inset, y0 + inset, x1 - inset, y1 - inset], radius=max(0, border_radius - inset), outline=border_color, width=2)
    
    return img

def pre_render_static_page(resolution: tuple, background_input: str, renderable_lines: list, line_positions: list, line_height: float, font_paths: dict, font_scale: float):
    """
    Renders the static components of a Mushaf page onto a single PIL Image.
    Static components: Background, Border, Surah Name, Basmallah, and Ayah text.
    """
    width, height = resolution
    img = get_pil_background(background_input, resolution)
    
    # --- Background Dimming ---
    try:
        dimming_opacity = float(config_manager.get("MUSHAF_BACKGROUND_DIMMING", "0.0"))
    except (ValueError, TypeError):
        dimming_opacity = 0.0
        
    if dimming_opacity > 0:
        # Create a black overlay
        overlay = Image.new('RGBA', resolution, (0, 0, 0, int(dimming_opacity * 255)))
        img.alpha_composite(overlay)
    # --------------------------

    bg_mode = config_manager.get("MUSHAF_PAGE_BACKGROUND_MODE", "Solid")
    bg_color = config_manager.get("MUSHAF_PAGE_COLOR", "#FFFDF5")
    try:
        opacity_percent = int(config_manager.get("MUSHAF_PAGE_OPACITY", "90"))
    except (ValueError, TypeError):
        opacity_percent = 90
    bg_opacity = int((opacity_percent / 100) * 255)
    
    # Top/Bottom margins for border height calculation
    top_margin = height * 0.1
    bottom_margin = height * 0.1
    usable_height = height - top_margin - bottom_margin
    
    # 1. Draw Border
    img = draw_mushaf_border_onto(img, usable_height, bg_mode, bg_color, bg_opacity)
    
    # 2. Draw Text Lines
    color = FONT_COLOR
    if isinstance(color, str) and color.startswith("rgb("):
        try:
            color = tuple(map(int, color.replace("rgb(", "").replace(")", "").split(",")))
        except:
            color = (255, 255, 255)
            
    for i, line in enumerate(renderable_lines):
        l_type = line.get("line_type", "ayah")
        y_pos = line_positions[i]
        
        # Determine text
        words = line.get("words", [])
        text = assemble_mushaf_line_text(words)
        
        font_path = font_paths.get("page")
        if l_type == "basmallah":
            font_path = font_paths.get("bsml")
            if not text: text = "\u00F3"
        elif l_type == "surah_name":
            font_path = font_paths.get("sura")
            surah_num = int(line["surah_number"])
            key = f"surah-{surah_num}"
            text = LIGATURE_DATA.get(key, str(surah_num))
            
        font_size = calculate_mushaf_font_size(width, line_height, l_type, font_scale)
        
        # Render text to temp image to get bounding box and handles
        text_img_arr = render_mushaf_text_to_image(text, font_path, font_size, color, (width, font_size))
        text_img = Image.fromarray(text_img_arr)
        
        # Center horizontally and vertically within the slot
        visual_h = text_img.height
        y_centered = calculate_centered_y(y_pos, line_height, visual_h, l_type)
        x_centered = (width - text_img.width) // 2
        
        # Paste onto main image
        img.paste(text_img, (int(x_centered), int(y_centered)), text_img)
        
    return img

def generate_image_background(background_image_url: str, duration: int, is_short: bool):
    resolution = get_resolution(is_short)
    background_image_url = edit_image(background_image_url, is_short)
    background_clip = ImageClip(background_image_url).set_opacity(BACKGROUND_OPACITY).set_duration(duration)
    return resize(background_clip, resolution)

def generate_video_background(video_path: str, duration: int, is_short: bool):
    resolution = get_resolution(is_short)
    clip = VideoFileClip(video_path)
    clip = clip.without_audio()
    try:
        speed = float(config_manager.get("VIDEO_BACKGROUND_SPEED", 1.0))
    except ValueError:
        speed = 1.0
    if speed != 1.0 and speed > 0:
        clip = clip.fx(vfx.speedx, speed)
    clip_aspect = clip.w / clip.h
    target_aspect = resolution[0] / resolution[1]
    if clip_aspect > target_aspect:
        clip = clip.resize(height=resolution[1])
        clip = clip.crop(x_center=clip.w/2, width=resolution[0])
    else:
        clip = clip.resize(width=resolution[0])
        clip = clip.crop(y_center=clip.h/2, height=resolution[1])
    clip = clip.set_opacity(BACKGROUND_OPACITY)
    if clip.duration < duration:
        clip = vfx.loop(clip, duration=duration)
    else:
        clip = clip.set_duration(duration)
    return clip

def hex_to_rgb(hex_color: str):
    """Converts a hex color string to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def generate_solid_background(duration: int, resolution: tuple, color=None):
    if color is None:
        color = BACKGROUND_RGB
    elif isinstance(color, str) and color.startswith('#'):
        color = hex_to_rgb(color)
    return ColorClip(size=resolution, color=color).set_duration(duration)

def generate_background(background_input: str, duration: int, is_short: bool, dimming: float = 0.0):
    resolution = get_resolution(is_short)
    
    # Use explicitly provided background_input first
    target_bg = background_input
    
    # If not provided, fallback to ACTIVE_BACKGROUND from global config
    if not target_bg:
        target_bg = config_manager.get("ACTIVE_BACKGROUND")
        
    base_clip = None
    if target_bg:
        if target_bg.startswith('#'):
            base_clip = generate_solid_background(duration, resolution, color=target_bg)
        elif target_bg.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            base_clip = generate_video_background(target_bg, duration, is_short)
        else:
            base_clip = generate_image_background(target_bg, duration, is_short)
    else:
        # Final fallback to solid BACKGROUND_RGB
        base_clip = generate_solid_background(duration, resolution)

    if dimming > 0:
        dim_clip = ColorClip(size=resolution, color=(0, 0, 0)).set_opacity(dimming).set_duration(duration)
        return CompositeVideoClip([base_clip, dim_clip])
    
    return base_clip

def generate_arabic_text_clip(text: str, is_short: bool, duration: int) -> TextClip:
    arabic_sizes = COMMON["f_arabic_size"](is_short, text)
    arabic_text_clip = TextClip(f"{text[:-1]} \u06DD{e2a(text)}", **arabic_sizes, **COMMON["arabic_textbox_config"])
    arabic_pos = COMMON["f_arabic_position"](is_short, arabic_text_clip.h)
    return arabic_text_clip.set_position(('center', arabic_pos)).set_duration(duration)

def generate_wbw_arabic_text_clip(words: list, ayah_num: int, is_short: bool, duration: float, segments: list) -> 'CompositeVideoClip':
    return generate_arabic_text_clip(" ".join(words), is_short, duration)

def generate_wbw_advanced_arabic_text_clip(text: str, is_short: bool, duration: float, font_size: int) -> TextClip:
    if is_short:
        size = (SHORT["width"] * 0.85, None)
    else:
        size = (LONG["width"] * 0.95, None)
    config = COMMON["arabic_textbox_config"].copy()
    config["fontsize"] = font_size
    config["size"] = size
    arabic_text_clip = TextClip(text, **config)
    arabic_pos = COMMON["f_arabic_position"](is_short, arabic_text_clip.h)
    return arabic_text_clip.set_position(('center', arabic_pos)).set_duration(duration)

def generate_wbw_advanced_translation_text_clip(text: str, is_short: bool, duration: float, font_size: int, font: str = None) -> TextClip:
    if is_short:
        size = (SHORT["width"] * 0.85, None)
    else:
        size = (LONG["width"] * 0.95, None)
    config = COMMON["translation_textbox_config"].copy()
    config["fontsize"] = font_size
    if font:
        config["font"] = get_font_path(font)
    config["size"] = size
    try:
        translation_clip = TextClip(text, **config)
    except Exception as e:
        translation_clip = ColorClip(size=(1,1), color=(0,0,0), duration=duration)
    translation_pos = COMMON["f_translation_position"](is_short)
    return translation_clip.set_position(('center', translation_pos)).set_duration(duration)

def generate_wbw_interlinear_text_clip(words: list, translations: list, is_short: bool, duration: float, arabic_font_size: int, translation_font_size: int, translation_font: str = None) -> CompositeVideoClip:
    space_width = 15
    arabic_config = COMMON["arabic_textbox_config"].copy()
    arabic_config["fontsize"] = arabic_font_size
    arabic_config.pop("size", None)
    arabic_config.pop("method", None)
    trans_config = COMMON["translation_textbox_config"].copy()
    trans_config["fontsize"] = translation_font_size
    if translation_font:
        trans_config["font"] = translation_font
    trans_config.pop("size", None)
    trans_config.pop("method", None)
    processed_blocks = []
    total_width = 0
    for i in range(len(words)):
        word = words[i]
        trans = translations[i] if i < len(translations) else ""
        ac = TextClip(word, **arabic_config)
        target_tw = ac.w + 40
        wrapped_trans_config = trans_config.copy()
        wrapped_trans_config["size"] = (target_tw, None)
        wrapped_trans_config["method"] = "caption"
        tc = TextClip(trans, **wrapped_trans_config)
        block_w = max(ac.w, tc.w, 0)
        color_str = COMMON["arabic_textbox_config"]["color"]
        if isinstance(color_str, str) and color_str.startswith("rgb("):
            try:
                color = tuple(map(int, color_str.replace("rgb(", "").replace(")", "").split(",")))
            except:
                color = (255, 255, 255)
        else:
            color = color_str
        uc = ColorClip(size=(ac.w, 3), color=color)
        processed_blocks.append({"ac": ac, "tc": tc, "uc": uc, "block_w": block_w})
        total_width += block_w
        if i < len(words) - 1:
            total_width += space_width
    max_ah = max((b["ac"].h for b in processed_blocks), default=0)
    max_th = max((b["tc"].h for b in processed_blocks), default=0)
    line_height = max_ah + 5 + 3 + 5 + max_th
    final_clips = []
    curr_x = total_width
    for block in processed_blocks:
        ac = block["ac"]
        tc = block["tc"]
        uc = block["uc"]
        block_w = block["block_w"]
        curr_x -= block_w
        ax = curr_x + (block_w - ac.w) // 2
        ay = 0 
        ac = ac.set_position((ax, ay))
        final_clips.append(ac)
        ux = ax
        uy = ay + ac.h + 2
        uc = uc.set_position((ux, uy))
        final_clips.append(uc)
        tx = curr_x + (block_w - tc.w) // 2
        ty = uy + 3 + 5
        tc = tc.set_position((tx, ty))
        final_clips.append(tc)
        curr_x -= space_width
    line_composite = CompositeVideoClip(final_clips, size=(total_width, line_height)).set_duration(duration)
    arabic_pos_y = COMMON["f_arabic_position"](is_short, line_height)
    return line_composite.set_position(('center', arabic_pos_y))

def generate_translation_text_clip(text: str, is_short: bool, duration: int) -> TextClip:
    translation_sizes = COMMON["f_translation_size"](is_short, text)
    translation_clip = TextClip(text, **translation_sizes, **COMMON["translation_textbox_config"])
    translation_pos = COMMON["f_translation_position"](is_short)
    return translation_clip.set_position(('center', translation_pos)).set_duration(duration)

def generate_full_ayah_translation_clip(text: str, is_short: bool, duration: int, font: str = None) -> TextClip:
    translation_sizes = COMMON["f_translation_size"](is_short, text)
    font_size = int(config_manager.get("WBW_FULL_TRANSLATION_FONT_SIZE", 30))
    config = COMMON["translation_textbox_config"].copy()
    config["fontsize"] = font_size
    if font:
        config["font"] = get_font_path(font)
    
    # Force center alignment for better looks in full translation
    config["align"] = "Center"
    
    # Ensure TextClip has duration
    translation_clip = TextClip(text, size=translation_sizes["size"], **config).set_duration(duration)
    
    # Add a semi-transparent background box
    bg_width = translation_clip.w + 40
    bg_height = translation_clip.h + 20
    bg_box = ColorClip(size=(bg_width, bg_height), color=(0, 0, 0)).set_opacity(0.6).set_duration(duration)
    
    # Composite them with explicit size and duration
    final_clip = CompositeVideoClip(
        [bg_box, translation_clip.set_position('center')],
        size=(bg_width, bg_height)
    ).set_duration(duration)
    
    translation_pos = COMMON["f_full_ayah_translation_position"](is_short)
    return final_clip.set_position(('center', translation_pos))

def generate_reciter_name_clip(reciter_name_bangla: str, is_short: bool, duration: int) -> TextClip:
    reciter_name_clip = TextClip(reciter_name_bangla, font=resolve_font_path("kalpurush"), **FOOTER_CONFIG)
    from processes.video_configs import get_reciter_info_position
    reciter_pos = get_reciter_info_position(is_short, reciter_name_clip.w)
    return reciter_name_clip.set_position(reciter_pos, relative=True).set_duration(duration)

def generate_surah_info_clip(surah_name: str, verse_number: int, is_short: bool, duration: int, language: str = "bengali"):
    verse_str = e2b(str(verse_number)) if language == "bengali" else str(verse_number)
    display_text = f'{surah_name} : {verse_str}' if verse_number > 0 else surah_name
    surah_name_clip = TextClip(display_text, font=resolve_font_path("kalpurush"), **FOOTER_CONFIG)
    from processes.video_configs import get_surah_info_position
    surah_pos = get_surah_info_position(is_short, surah_name_clip.w)
    return surah_name_clip.set_position(surah_pos, relative=True).set_duration(duration)

def generate_brand_clip(brand_name: str, is_short: bool, duration: int) -> TextClip:
    brand_name_clip = TextClip(brand_name, font=resolve_font_path("kalpurush"), **FOOTER_CONFIG)
    from processes.video_configs import get_channel_info_position
    brand_pos = get_channel_info_position(is_short, brand_name_clip.w)
    return brand_name_clip.set_position(brand_pos, relative=True).set_duration(duration)

def generate_mushaf_border_clip(size: tuple, thickness: int, radius: int, color: tuple, padding: int, duration: float, bg_mode: str = "Solid", bg_color: str = "#FFFDF5", bg_opacity: int = 255) -> ImageClip:
    """
    Generates an authentic multi-layered Mushaf border clip with rounded corners.
    Includes a double border (thick outer, thin inner) and a customizable background.
    """
    # 1. Create Canvas
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 2. Handle Background Mode
    # Default to Solid Cream if mode not recognized
    opacity = 255
    if bg_mode == "Transparent":
        opacity = 0
    elif bg_mode in ["Semi-Transparent", "Semi"]:
        opacity = bg_opacity
    
    if opacity > 0:
        fill_rgb = hex_to_rgb(bg_color)
        fill_rgba = fill_rgb + (opacity,)
        draw.rounded_rectangle([0, 0, size[0], size[1]], radius=radius, fill=fill_rgba)
    
    # 3. Apply Subtle Paper Texture (Noise) - ONLY IN SOLID OR SEMI MODE
    if bg_mode in ["Solid", "Semi-Transparent", "Semi"]:
        # Convert to numpy to apply lightweight noise
        arr = np.array(img)
        # Only apply noise if opacity is significant enough to see it
        if opacity > 50:
            noise = np.random.randint(-5, 5, (size[1], size[0], 3), dtype='int16')
            # Only apply to non-transparent pixels (the paper area)
            mask = arr[..., 3] > 0
            arr[mask, :3] = np.clip(arr[mask, :3] + noise[mask], 0, 255).astype('uint8')
        img = Image.fromarray(arr)
        draw = ImageDraw.Draw(img)

    # 4. Draw Outer Thick Border
    half_th = thickness // 2
    outer_box = [half_th, half_th, size[0] - half_th, size[1] - half_th]
    draw.rounded_rectangle(outer_box, radius=radius, outline=color, width=thickness)
    
    # 5. Draw Inner Thin Border
    # Inset by a reasonable margin (e.g., 12px)
    inset = thickness + 6
    inner_box = [inset, inset, size[0] - inset, size[1] - inset]
    draw.rounded_rectangle(inner_box, radius=max(0, radius - inset), outline=color, width=2)
    
    # Convert to MoviePy ImageClip
    img_arr = np.array(img)
    return ImageClip(img_arr).set_duration(duration)

def calculate_mushaf_content_y_positions(height: int, num_lines: int, has_header_gap: bool) -> list:
    """
    Calculates the Y positions for Mushaf lines to ensure the content block is centered.
    """
    line_height = (height * 0.8) / 15
    gap = 20 if has_header_gap else 0
    
    total_content_height = (num_lines * line_height) + gap
    start_y = (height / 2) - (total_content_height / 2)
    
    positions = []
    current_y = start_y
    for i in range(num_lines):
        positions.append(current_y)
        current_y += line_height
        if i == 0 and has_header_gap:
            current_y += gap
            
    return positions

def calculate_centered_y(y_pos: float, line_height: float, visual_h: int, l_type: str) -> float:
    """
    Calculates the Y position to center text within its slot.
    """
    y_centered = y_pos + (line_height / 2) - (visual_h / 2)
    
    # Authenticity Adjustment: Both QCF_BSML and QCF_SurahHeader have internal 
    # metrics that make them sit slightly high when visually centered based on bbox.
    # Shifting down by ~2 pixels for standard line heights provides visual parity.
    if l_type in ["basmallah", "surah_name"]:
         # Authenticity Adjustment: These fonts have metrics that make them sit high.
         # Shifting down by ~1.2% of line_height compensates for this.
         y_centered += (line_height * 0.012)
         
    return y_centered

def calculate_mushaf_border_width(screen_width: int, border_width_percent: int) -> int:
    """
    Calculates the width of the Mushaf border based on screen width and percentage.
    """
    return int(screen_width * (border_width_percent / 100))

def calculate_mushaf_font_size(width: int, line_height: float, l_type: str, scale_factor: float = 1.0) -> int:
    """
    Calculates the font size based on line type and scaling.
    """
    if l_type == "surah_name":
        # Web uses 15cqw (~15% of width).
        if width == 1080:
            return int(width * 0.35)
        return int(width * 0.15)
    elif l_type == "basmallah":
        # Basmallah should be smaller, matching web ratio of ~1.9x standard text (0.7 * 1.9 = 1.33)
        return int(line_height * 1.3)
    else:
        # Standard Ayah text
        # Baseline was 0.7 * line_height
        return int(line_height * 0.7 * scale_factor)

def generate_mushaf_page_clip(lines: list, page_number: int, is_short: bool, duration: float, background_input: str = None) -> CompositeVideoClip:

    """

    Generates a CompositeVideoClip for a Mushaf page using Static Flattening.

    Combines background, border, and all static text into a single pre-rendered ImageClip.

    """

    resolution = get_resolution(is_short)

    width, height = resolution

    

    font_paths = {

        "page": os.path.abspath(os.path.join("QPC_V2_Font.ttf", f"p{page_number}.ttf")),

        "bsml": os.path.abspath(os.path.join("QPC_V2_Font.ttf", "QCF_BSML.TTF")),

        "sura": os.path.abspath(os.path.join("QPC_V2_Font.ttf", "QCF_SurahHeader_COLOR-Regular.ttf"))

    }

    

    # Fallback for page font

    if not os.path.exists(font_paths["page"]):

        font_paths["page"] = "Arial"



    top_margin = height * 0.1

    bottom_margin = height * 0.1

    usable_height = height - top_margin - bottom_margin

    line_height = usable_height / 15

    

    # 1. Filter renderable lines
    renderable_lines = []
    for line in lines:
        l_type = line.get("line_type", "ayah")
        words = line.get("words", [])
        text = assemble_mushaf_line_text(words)
        if l_type == "basmallah" and not text:
            text = "\u00F3"
        if not text and l_type != "surah_name":
            continue
        renderable_lines.append(line)



    if not renderable_lines:

        return ColorClip(size=resolution, color=(0,0,0)).set_opacity(0).set_duration(duration)



    # 2. Calculate Positions

    has_header = any(l.get("line_type") == "surah_name" for l in renderable_lines)

    has_bsml = any(l.get("line_type") == "basmallah" for l in renderable_lines)

    has_header_gap = has_header and has_bsml

    line_positions = calculate_mushaf_content_y_positions(height, len(renderable_lines), has_header_gap)

    

    # 3. Font Scale

    try:

        font_scale = float(config_manager.get("MUSHAF_FONT_SCALE", "0.8"))

    except (ValueError, TypeError):

        font_scale = 0.8



    # 4. Pre-render Static Image (Background + Border + Static Text)

    static_img = pre_render_static_page(

        resolution=resolution,

        background_input=background_input,

        renderable_lines=renderable_lines,

        line_positions=line_positions,

        line_height=line_height,

        font_paths=font_paths,

        font_scale=font_scale

    )

    

    # Create the base static layer

    static_clip = ImageClip(np.array(static_img)).set_duration(duration)

    clips = [static_clip]

    

    # 5. Add Dynamic Highlighting Layers

    for i, line in enumerate(renderable_lines):

        l_type = line.get("line_type", "ayah")

        if l_type in ["basmallah", "surah_name"]:

            continue # No highlighting for headers

            

        start_ms = line.get("start_ms")

        end_ms = line.get("end_ms")

        

        if start_ms is not None and end_ms is not None:

            try:

                start_sec = max(0, float(start_ms) / 1000.0)

                end_sec = min(duration, float(end_ms) / 1000.0)

                if start_sec < duration:

                    h_duration = min(end_sec - start_sec, duration - start_sec)

                    if h_duration > 0.05:
                        # For dynamic width calculation, we need to know the rendered text width
                        # Since we flattened it, we must re-calculate or approximate.
                        # For consistency, we'll re-calculate width once per highlighted line
                        words = line.get("words", [])
                        text = assemble_mushaf_line_text(words)
                        font_size = calculate_mushaf_font_size(width, line_height, l_type, font_scale)
                        
                        # Use PIL to get text width accurately
                        cache_key = f"{font_paths['page']}_{font_size}"
                        font = FONT_CACHE.get(cache_key) or ImageFont.truetype(font_paths['page'], font_size)

                        

                        # Draw dummy to get bbox

                        dummy_img = Image.new('RGBA', (width, int(line_height)), (0,0,0,0))

                        d = ImageDraw.Draw(dummy_img)

                        bbox = d.textbbox((0, 0), text, font=font)

                        text_w = bbox[2] - bbox[0]

                        

                        h_width = text_w + 20

                        h_clip = ColorClip(size=(h_width, int(line_height)), color=(255, 255, 0)).set_opacity(0.1).set_start(start_sec).set_duration(h_duration).set_position(('center', line_positions[i]))

                        clips.append(h_clip)

            except (ValueError, TypeError):

                pass

    

    return CompositeVideoClip(clips, size=resolution).set_duration(duration)
