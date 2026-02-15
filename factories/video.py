import numpy as np
import os
from moviepy.editor import AudioClip, AudioFileClip
from processes.video_configs import (
    SHORT, LONG, COMMON
)

def make_silence(duration, fps=44100):
    return AudioClip(make_frame=lambda t: np.zeros((1,)), duration=duration, fps=fps)

def get_standard_basmallah_clip():
    """Returns an AudioFileClip for the standardized Basmallah audio."""
    path = "recitation_data/basmalah.mp3"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Standard Basmallah audio not found at {path}")
    return AudioFileClip(path)

def get_resolution(is_short: bool) -> tuple:
    return (SHORT["width"], SHORT["height"]) if is_short else (LONG["width"], LONG["height"])

def fetch_background_image():
    return COMMON["bg_image"]
