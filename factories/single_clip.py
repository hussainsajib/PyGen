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
    This is often more reliable for PUA glyphs than MoviePy's TextClip.
    """
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"DEBUG: PIL failed to load font {font_path}: {e}")
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    draw.text((x, y), text, font=font, fill=color)
    return np.array(img)

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

def generate_solid_background(duration: int, resolution: tuple):
    return ColorClip(size=resolution, color=BACKGROUND_RGB).set_duration(duration)

def generate_background(background_image_url: str, duration: int, is_short: bool):
    resolution = get_resolution(is_short)
    if background_image_url:
        if background_image_url.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            return generate_video_background(background_image_url, duration, is_short)
        return generate_image_background(background_image_url, duration, is_short)
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

def generate_mushaf_page_clip(lines: list, page_number: int, is_short: bool, duration: float) -> CompositeVideoClip:
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
    
    color = FONT_COLOR
    if isinstance(color, str) and color.startswith("rgb("):
        try:
            color = tuple(map(int, color.replace("rgb(", "").replace(")", "").split(",")))
        except:
            color = (255, 255, 255)

    for i, line in enumerate(lines):
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
            # If the text is missing in DB for basmallah lines (which happens in some DBs), 
            # we might need to hardcode the special char if the font requires it.
            # However, assuming the DB has the correct text or the font works with standard text.
            if not text:
                 # Fallback if text is empty but type is basmallah, usually it's "بسم الله الرحمن الرحيم"
                 text = "بسم الله الرحمن الرحيم"
        elif l_type == "surah_name":
            current_font_path = font_path_sura
            if not text:
                try:
                    from processes.Classes.surah import Surah
                    s_obj = Surah(line["surah_number"])
                    # For SurahHeader fonts, often the glyph is mapped to the surah number as a character
                    # We try the character mapping first for this specific font
                    text = chr(line["surah_number"]) 
                except Exception as e:
                    print(f"Error mapping surah number to char: {e}")
                    text = str(line["surah_number"])

        if not text:
            continue
            
        y_pos = top_margin + (i * line_height)
        font_size = int(line_height * 0.7)
        
        # Adjust font size/y_pos for headers if needed? 
        # Usually headers are same line height.
        
        # Render
        img_array = render_mushaf_text_to_image(text, current_font_path, font_size, color, (int(width * 0.9), int(line_height)))
        
        # Check if render produced anything visible (alpha channel check)
        # If QCF_SurahHeader... failed with character mapping, try Arabic Name with Arial
        if l_type == "surah_name" and not np.any(img_array[..., 3] > 0):
            print(f"[DEBUG] Surah header font failed for char {ord(text) if text else 'N/A'}. Trying Arabic Name with Arial.")
            try:
                from processes.Classes.surah import Surah
                s_obj = Surah(line["surah_number"])
                text = " ".join(reversed(s_obj.arabic_name.split())) if s_obj.arabic_name else s_obj.english_name
            except:
                text = str(line["surah_number"])
            img_array = render_mushaf_text_to_image(text, "arial.ttf", font_size, color, (int(width * 0.9), int(line_height)))
            
        t_clip = ImageClip(img_array).set_duration(duration).set_position(('center', y_pos))
        clips.append(t_clip)
        start_ms = line.get("start_ms")
        end_ms = line.get("end_ms")
        if start_ms is not None and end_ms is not None:
            try:
                start_sec = float(start_ms) / 1000.0
                end_sec = float(end_ms) / 1000.0
                if start_sec < duration:
                    h_duration = min(end_sec - start_sec, duration - start_sec)
                    if h_duration > 0.05:
                        h_clip = ColorClip(size=(int(width * 0.95), int(line_height)), color=(255, 255, 0)).set_opacity(0.3).set_start(start_sec).set_duration(h_duration).set_position(('center', y_pos))
                        clips.append(h_clip)
            except (ValueError, TypeError):
                pass
    if not clips:
        return ColorClip(size=resolution, color=(0,0,0)).set_opacity(0).set_duration(duration)
    return CompositeVideoClip(clips, size=resolution).set_duration(duration)