from processes.video_configs import (
    SHORT, LONG, COMMON
)

def get_resolution(is_short: bool) -> tuple:
    return (SHORT["width"], SHORT["height"]) if is_short else (LONG["width"], LONG["height"])

def fetch_background_image():
    return COMMON["bg_image"]
