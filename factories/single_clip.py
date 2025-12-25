from factories.video import get_resolution
from factories.image import edit_image
from moviepy.editor import ImageClip, ColorClip, TextClip
from moviepy.video.fx.resize import resize
from convert_numbers import english_to_arabic as e2a
from bangla import convert_english_digit_to_bangla_digit as e2b
from processes.video_configs import BACKGROUND_OPACITY, BACKGROUND_RGB, COMMON, FOOTER_CONFIG

def generate_image_background(background_image_url: str, duration: int, is_short: bool):
    resolution = get_resolution(is_short)
    background_image_url = edit_image(background_image_url, is_short)
    background_clip = ImageClip(background_image_url).set_opacity(BACKGROUND_OPACITY).set_duration(duration)
    return resize(background_clip, resolution)

def generate_solid_background(duration: int, resolution: tuple):
    return ColorClip(size=resolution, color=BACKGROUND_RGB).set_duration(duration)


def generate_background(background_image_url: str, duration: int, is_short: bool):
    resolution = get_resolution(is_short)
    if background_image_url:
        return generate_image_background(background_image_url, duration, is_short)
    return generate_solid_background(duration, resolution)

def generate_arabic_text_clip(text: str, is_short: bool, duration: int) -> TextClip:
    arabic_sizes = COMMON["f_arabic_size"](is_short, text)
    arabic_text_clip = TextClip(f"{text[:-1]} \u06DD{e2a(text)}", **arabic_sizes, **COMMON["arabic_textbox_config"])
    arabic_pos = COMMON["f_arabic_position"](is_short, arabic_text_clip.h)
    arabic_text_clip = arabic_text_clip.set_position(('center', arabic_pos))\
                        .set_duration(duration)
    return arabic_text_clip

def generate_translation_text_clip(text: str, is_short: bool, duration: int) -> TextClip:
    translation_sizes = COMMON["f_translation_size"](is_short, text)
    translation_clip = TextClip(text, **translation_sizes, **COMMON["translation_textbox_config"])
    translation_pos = COMMON["f_translation_position"](is_short)
    translation_clip = translation_clip.set_position(('center', translation_pos))\
                        .set_duration(duration)
    return translation_clip

def generate_reciter_name_clip(reciter_name_bangla: str, is_short: bool, duration: int) -> TextClip:
    reciter_name_clip = TextClip(reciter_name_bangla, font="kalpurush", **FOOTER_CONFIG)
    reciter_pos = COMMON["f_reciter_info_position"](is_short, reciter_name_clip.w)
    reciter_name_clip = reciter_name_clip.set_position(reciter_pos, relative=True)\
                    .set_duration(duration)
    return reciter_name_clip

def generate_surah_info_clip(surah_name_bangla: str, verse_number: int, is_short: bool, duration: int):
    surah_name_clip = TextClip(f'{surah_name_bangla} : {e2b(str(verse_number))}', font="kalpurush", **FOOTER_CONFIG)
    surah_pos = COMMON["f_surah_info_position"](is_short, surah_name_clip.w)
    surah_name_clip = surah_name_clip.set_position(surah_pos, relative=True)\
                    .set_duration(duration)
    return surah_name_clip

def generate_brand_clip(brand_name: str, is_short: bool, duration: int) -> TextClip:
    brand_name_clip = TextClip(brand_name, font="kalpurush", **FOOTER_CONFIG)
    brand_pos = COMMON["f_channel_info_position"](is_short, brand_name_clip.w)
    brand_name_clip = brand_name_clip.set_position(brand_pos, relative=True)\
                    .set_duration(duration)
    return brand_name_clip