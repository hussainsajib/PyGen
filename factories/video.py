import numpy as np
from moviepy.editor import AudioClip
from processes.video_configs import (
    SHORT, LONG, COMMON
)

def make_silence(duration, fps=44100):
    return AudioClip(make_frame=lambda t: np.zeros((1,)), duration=duration, fps=fps)

def get_resolution(is_short: bool) -> tuple:
    return (SHORT["width"], SHORT["height"]) if is_short else (LONG["width"], LONG["height"])

def fetch_background_image():
    return COMMON["bg_image"]
