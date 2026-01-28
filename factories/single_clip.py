from factories.video import get_resolution
from factories.image import edit_image
from moviepy.editor import ImageClip, ColorClip, TextClip, CompositeVideoClip, VideoFileClip, vfx
from moviepy.video.fx.resize import resize
from convert_numbers import english_to_arabic as e2a
from bangla import convert_english_digit_to_bangla_digit as e2b
from processes.video_configs import BACKGROUND_OPACITY, BACKGROUND_RGB, COMMON, FOOTER_CONFIG, SHORT, LONG, FONT_COLOR
from config_manager import config_manager
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import json

# Load ligature data for Mushaf headers
LIGATURE_DATA = {}
try:
    ligature_path = os.path.abspath(os.path.join("databases", "text", "ligatures.json"))
    if os.path.exists(ligature_path):
        with open(ligature_path, "r", encoding="utf-8") as f:
            LIGATURE_DATA = json.load(f)
except Exception as e:
    print(f"[ERROR] Failed to load ligatures.json: {e}")

def get_font_path(font_name: str) -> str:
    """Checks for a font in a local 'fonts' directory, otherwise returns the name."""
    if font_name and font_name.endswith(".ttf"):
        local_path = os.path.join("fonts", font_name)
        if os.path.exists(local_path):
            return os.path.abspath(local_path)
    return font_name 

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
    try:
        font = ImageFont.truetype(font_path, font_size)
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

def generate_background(background_input: str, duration: int, is_short: bool):
    resolution = get_resolution(is_short)
    
    # Use explicitly provided background_input first
    target_bg = background_input
    
    # If not provided, fallback to ACTIVE_BACKGROUND from global config
    if not target_bg:
        target_bg = config_manager.get("ACTIVE_BACKGROUND")
        
    if target_bg:
        if target_bg.startswith('#'):
            return generate_solid_background(duration, resolution, color=target_bg)
        if target_bg.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            return generate_video_background(target_bg, duration, is_short)
        return generate_image_background(target_bg, duration, is_short)
        
    # Final fallback to solid BACKGROUND_RGB
    return generate_solid_background(duration, resolution)

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
    translation_clip = TextClip(text, size=translation_sizes["size"], **config)
    translation_pos = COMMON["f_full_ayah_translation_position"](is_short)
    return translation_clip.set_position(('center', translation_pos)).set_duration(duration)

def generate_reciter_name_clip(reciter_name_bangla: str, is_short: bool, duration: int) -> TextClip:
    reciter_name_clip = TextClip(reciter_name_bangla, font="kalpurush", **FOOTER_CONFIG)
    reciter_pos = COMMON["f_reciter_info_position"](is_short, reciter_name_clip.w)
    return reciter_name_clip.set_position(reciter_pos, relative=True).set_duration(duration)

def generate_surah_info_clip(surah_name: str, verse_number: int, is_short: bool, duration: int, language: str = "bengali"):
    verse_str = e2b(str(verse_number)) if language == "bengali" else str(verse_number)
    surah_name_clip = TextClip(f'{surah_name} : {verse_str}', font="kalpurush", **FOOTER_CONFIG)
    surah_pos = COMMON["f_surah_info_position"](is_short, surah_name_clip.w)
    return surah_name_clip.set_position(surah_pos, relative=True).set_duration(duration)

def generate_brand_clip(brand_name: str, is_short: bool, duration: int) -> TextClip:
    brand_name_clip = TextClip(brand_name, font="kalpurush", **FOOTER_CONFIG)
    brand_pos = COMMON["f_channel_info_position"](is_short, brand_name_clip.w)
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
         
    return y_centered

def generate_mushaf_page_clip(lines: list, page_number: int, is_short: bool, duration: float, background_input: str = None) -> CompositeVideoClip:
    """
    Generates a CompositeVideoClip for a Mushaf page.
    """
    resolution = get_resolution(is_short)
    width, height = resolution
    font_path_page = os.path.abspath(os.path.join("QPC_V2_Font.ttf", f"p{page_number}.ttf"))
    font_path_bsml = os.path.abspath(os.path.join("QPC_V2_Font.ttf", "QCF_BSML.TTF"))
    font_path_sura = os.path.abspath(os.path.join("QPC_V2_Font.ttf", "QCF_SurahHeader_COLOR-Regular.ttf"))

    if not os.path.exists(font_path_page):
        font_path_page = "Arial" 

    top_margin = height * 0.1
    bottom_margin = height * 0.1
    usable_height = height - top_margin - bottom_margin
    line_height = usable_height / 15
    clips = []
    
    # 0. Generate Global Background (Bottom-most layer)
    bg_clip = generate_background(background_input, duration, is_short)
    if bg_clip:
        clips.append(bg_clip)
    
    # Get internal Mushaf background settings from config
    bg_mode = config_manager.get("MUSHAF_PAGE_BACKGROUND_MODE", "Solid")
    bg_color = config_manager.get("MUSHAF_PAGE_COLOR", "#FFFDF5")
    
    # Calculate alpha for Semi mode
    try:
        opacity_percent = int(config_manager.get("MUSHAF_PAGE_OPACITY", "90"))
    except (ValueError, TypeError):
        opacity_percent = 90
    bg_opacity = int((opacity_percent / 100) * 255)

    # Calculate positions
    has_header = any(l.get("line_type") == "surah_name" for l in lines)
    has_bsml = any(l.get("line_type") == "basmallah" for l in lines)
    has_header_gap = has_header and has_bsml
    
    # Filter renderable lines to ensure accurate centering count
    renderable_lines = []
    for line in lines:
        l_type = line.get("line_type", "ayah")
        words = line.get("words", [])
        text = "".join([w["text"] for w in reversed(words)])
        if l_type == "basmallah" and not text:
            text = "\u00F3"
        if not text and l_type != "surah_name":
            continue
        renderable_lines.append(line)

    line_positions = calculate_mushaf_content_y_positions(height, len(renderable_lines), has_header_gap)

    # 1. Generate Authentic Static Border
    # Dimensions: FIXED 50% width for consistency
    border_w = int(width * 0.50)
    border_h = int(usable_height + 60) # Generous height to encompass all slots
    border_color = (212, 197, 161) # Authentic Gold/Bronze
    border_thickness = 8
    border_radius = 25
    
    border_clip = generate_mushaf_border_clip(
        size=(border_w, border_h),
        thickness=border_thickness,
        radius=border_radius,
        color=border_color,
        padding=25,
        duration=duration,
        bg_mode=bg_mode,
        bg_color=bg_color,
        bg_opacity=bg_opacity
    )    
    # Position the border centered vertically on the frame
    border_y = (height / 2) - (border_h / 2)
    clips.append(border_clip.set_position(('center', border_y)))

    color = FONT_COLOR
    if isinstance(color, str) and color.startswith("rgb("):
        try:
            color = tuple(map(int, color.replace("rgb(", "").replace(")", "").split(",")))
        except:
            color = (255, 255, 255)

    for i, line in enumerate(renderable_lines):
        # Reverse words for RTL rendering
        words = line.get("words", [])
        text = "".join([w["text"] for w in reversed(words)])
        
        # Determine font based on line type
        l_type = line.get("line_type", "ayah")
        current_font_path = font_path_page
        
        if l_type == "basmallah":
            current_font_path = font_path_bsml
            # For Bismillah, the text in DB might be standard Arabic, 
            # but the font might map specific codepoints or handle it nicely.
            if not text:
                 text = "بسم الله الرحمن الرحيم"
            
            # Authenticity Refinement: QCF_BSML.TTF uses U+00F3 for the full calligraphy
            if "QCF_BSML" in current_font_path:
                text = "\u00F3" # U+00F3

        elif l_type == "surah_name":
            current_font_path = font_path_sura
            # We will determine the text inside the render loop to allow retries with different mappings
            text = None 

        y_pos = line_positions[i]
        
        if l_type in ["surah_name", "basmallah"]:
            # Capture detail, but trimming ensures it fits
            if l_type == "surah_name":
                # Web uses 15cqw (~15% of width). 
                # 15% of frame width provides direct parity.
                font_size = int(width * 0.15)
            else:
                # Basmallah should be smaller, matching web ratio of ~1.9x standard text (0.7 * 1.9 = 1.33)
                font_size = int(line_height * 1.3)
            
            if l_type == "surah_name":
                # Use ligature data from ligatures.json
                surah_num = int(line["surah_number"])
                key = f"surah-{surah_num}"
                text_candidate = LIGATURE_DATA.get(key, str(surah_num))
                img_array = render_mushaf_text_to_image(text_candidate, current_font_path, font_size, color, (width, font_size))
            else:
                # Basmallah
                img_array = render_mushaf_text_to_image(text, current_font_path, font_size, color, (width, font_size))
            
            # Position centered vertically on the line slot
            visual_h = img_array.shape[0]
            y_centered = calculate_centered_y(y_pos, line_height, visual_h, l_type)
        else:
            font_size = int(line_height * 0.7)
            img_array = render_mushaf_text_to_image(text, current_font_path, font_size, color, (int(width * 0.9), int(line_height)))
            
            visual_h = img_array.shape[0]
            y_centered = calculate_centered_y(y_pos, line_height, visual_h, l_type)

        t_clip = ImageClip(img_array).set_position(('center', int(y_centered))).set_duration(duration)
        # print(f"DEBUG: {l_type} at y_centered={y_centered}")
        
        # Apply highlighting logic ONLY if timestamps are provided and it's an ayah
        start_ms = line.get("start_ms")
        end_ms = line.get("end_ms")
        
        if start_ms is not None and end_ms is not None:
            # Apply highlighting logic - EXCLUDING Basmallah and Surah Headers
            if l_type not in ["basmallah", "surah_name"]:
                try:
                    start_sec = max(0, float(start_ms) / 1000.0)
                    end_sec = min(duration, float(end_ms) / 1000.0)
                    if start_sec < duration:
                        h_duration = min(end_sec - start_sec, duration - start_sec)
                        if h_duration > 0.05:
                            # Dynamic highlight width based on text image + padding
                            h_width = img_array.shape[1] + 20
                            h_clip = ColorClip(size=(h_width, int(line_height)), color=(255, 255, 0)).set_opacity(0.3).set_start(start_sec).set_duration(h_duration).set_position(('center', y_pos))
                            clips.append(h_clip)
                except (ValueError, TypeError):
                    pass

        clips.append(t_clip)
    if not clips:
        return ColorClip(size=resolution, color=(0,0,0)).set_opacity(0).set_duration(duration)
    
    return CompositeVideoClip(clips, size=resolution).set_duration(duration)