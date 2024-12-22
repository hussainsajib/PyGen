QURAN_API_URL = "https://api.alquran.cloud/v1/ayah/{surah}:{verse}"
TRANSLATION_URL = "https://api.quran.com/api/v4/verses/by_key/{surah}:{verse}?translations=161"
AUDIO_API_URL = "https://api.alquran.cloud/v1/ayah/{surah}:{verse}/{reciter}"
IMAGE_API_URL = "https://api.unsplash.com/photos/random?query=universe&orientation=landscape&client_id=gvKXwU6tDDoZl6N3O1YWUIrT19yqZZW6CQLlSEGoxew"
RECITER="ar.alafasy"
FONT_COLOR = "white"
BACKGROUND = "background/dawn.jpg"
BACKGROUND_RGB = (7, 107, 40) #black (0, 0, 0)
BACKGROUND_OPACITY = 0.5

TARGET_HEIGHT = 1080
TARGET_WIDTH = 1920
TARGET_RESOLUTION = (TARGET_WIDTH, TARGET_HEIGHT)
MAIN_BOXES_HEIGHT = None
MAIN_BOXES_WIDTH = 1600
MAIN_TEXT_BOXES_SIZE=(MAIN_BOXES_WIDTH, MAIN_BOXES_HEIGHT)
ARABIC_TEXT_CLIP_POS = ('center', (TARGET_HEIGHT // 2) - 450)
TRANS_TEXT_CLIP_POS = ('center', (TARGET_HEIGHT // 2) + 50)
FOOTER_CONFIG = {
    "fontsize": 30, 
    "color": FONT_COLOR
}

INTRO_DURATION = 4

def get_arabic_text_position(is_short: bool, text_clip_height: int):
    if is_short:
        return (SHORT["height"] // 2) - (text_clip_height + 25)
    return (LONG["height"] // 2) - (text_clip_height + 25)


def get_translation_text_position(is_short: bool):
    if is_short:
        return (SHORT["height"] // 2) + 50
    return (LONG["height"] // 2) + 25

def get_reciter_info_position(is_short: bool, clip_width: int):
    if is_short:
        return ((SHORT["width"] - clip_width) / (SHORT["width"] * 2), 0.05)
    return (0.05, 0.92)

def get_surah_info_position(is_short: bool, clip_width: int):
    if is_short:
        return ((SHORT["width"] - clip_width) / (SHORT["width"] * 2), 0.07)
    return ((LONG["width"] - clip_width) / (LONG["width"] * 2), 0.92)

def get_channel_info_position(is_short: bool, clip_width: int):
    if is_short:
        return ((SHORT["width"] - clip_width) / (SHORT["width"] * 2), 0.09)
    return (0.85, 0.92)

def get_arabic_textbox_size(is_short: bool):
    if is_short:
        return {
            "size": (SHORT["width"] * 0.85, None),
            "fontsize": 60
        }
    return {
        "size": (LONG["width"] * 0.85, None),
        "fontsize": 70
    }

def get_translation_textbox_size(is_short: bool):
    if is_short:
        return {
            "size": (SHORT["width"] * 0.85, None),
            "fontsize": 30
        }
    return {
        "size": (LONG["width"] * 0.85, None),
        "fontsize": 40
    }

COMMON = {
    "long_side": 1920,
    "short_side": 1080,
    "font_color": "white",
    "is_solid_bg": True,
    "bg_image": "background/makkah.jpg",
    "enable_intro": True,
    "enable_outro": True,
    "enable_title": True,
    "enable_subtitle": True,
    "enable_footer": True,
    "enable_reciter_info": True,
    "enable_surah_info": True,
    "enable_channel_info": True,
    "f_arabic_position": get_arabic_text_position,
    "f_translation_position": get_translation_text_position,
    "f_reciter_info_position": get_reciter_info_position,
    "f_surah_info_position": get_surah_info_position,
    "f_channel_info_position": get_channel_info_position,
    "f_arabic_size": get_arabic_textbox_size,
    "f_translation_size": get_translation_textbox_size,
    "arabic_textbox_config": {
        "color": FONT_COLOR, 
        "method": 'caption',
        "font": "KFGQPC Uthmanic Script Regular",
        "interline": 4
    },
    "translation_textbox_config": {
        "color": FONT_COLOR, 
        "font": 'Kalpurush', 
        "method": 'caption', 
        "interline": 4
    }
}
LONG = {
    "height": COMMON["short_side"],
    "width": COMMON["long_side"],
    "intro": {
        "title": {
            "size": 0,
            "position": 0,
            "color": COMMON["font_color"]
        },
        "subtitle": {
            "size": 0,
            "position": 0,
            "color": COMMON["font_color"]
        }
    },
    "video": {
        "main": {
            "size": 0,
            "position": ('center', (COMMON["short_side"] // 2) - 450),
            "height": None,
            "width": 1600,
            "color": COMMON["font_color"]
        },
        "subtext": {
            "size": 0,
            "position": ('center', (COMMON["short_side"] // 2) + 50),
            "height": None,
            "width": 1600,
            "color": COMMON["font_color"]
        },
        "footer": {
            "reciter": {
                "size": 0,
                "position": 0,
                "color": COMMON["font_color"]
            },
            "surah": {
                "size": 0,
                "position": 0,
                "color": COMMON["font_color"]
            },
            "channel": {
                "size": 0,
                "position": 0,
                "color": COMMON["font_color"]
            }
        }
    },
    "outro": {
        "size": 0,
        "position": 0,
        "color": COMMON["font_color"]
    }
}
SHORT = {
    "height": COMMON["long_side"],
    "width": COMMON["short_side"],
    "intro": {
        "title": {
            "size": 0,
            "position": 0,
            "color": COMMON["font_color"]
        },
        "subtitle": {
            "size": 0,
            "position": 0,
            "color": COMMON["font_color"]
        }
    },
    "video": {
        "main": {
            "size": 0,
            "position": ('center', (COMMON["short_side"] // 2) - 450),
            "height": None,
            "width": 1600,
            "color": COMMON["font_color"]
        },
        "subtext": {
            "size": 0,
            "position": ('center', (COMMON["short_side"] // 2) + 50),
            "height": None,
            "width": 1600,
            "color": COMMON["font_color"]
        },
        "footer": {
            "reciter": {
                "size": 0,
                "position": 0,
                "color": COMMON["font_color"]
            },
            "surah": {
                "size": 0,
                "position": 0,
                "color": COMMON["font_color"]
            },
            "channel": {
                "size": 0,
                "position": 0,
                "color": COMMON["font_color"]
            }
        }
    },
    "outro": {
        "size": 0,
        "position": 0,
        "color": COMMON["font_color"]
    }
}