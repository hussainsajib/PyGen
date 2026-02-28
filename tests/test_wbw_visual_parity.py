import pytest
import numpy as np
import os
from PIL import Image
from factories.wbw_fast_render import WBWFastRenderer
from processes.video_configs import COMMON, SHORT, LONG
from factories.single_clip import (
    generate_wbw_advanced_arabic_text_clip, 
    generate_wbw_advanced_translation_text_clip,
    generate_wbw_interlinear_text_clip
)
from moviepy.editor import CompositeVideoClip, ColorClip
from factories.video import get_resolution

def get_moviepy_standard_frame(scene_data):
    is_short = scene_data.get("is_short", False)
    res = get_resolution(is_short)
    duration = (scene_data["end_ms"] - scene_data["start_ms"]) / 1000.0
    
    # 1. Background
    bg = ColorClip(size=res, color=(0,0,0)).set_duration(duration)
    
    # 2. Arabic
    arabic_text = " ".join(scene_data["words"])
    # Standard font size for regular is 65 (from get_arabic_textbox_size)
    font_size = 65
    ac = generate_wbw_advanced_arabic_text_clip(arabic_text, is_short, duration, font_size)
    
    # 3. Translation
    trans_text = " ".join(scene_data["translations"])
    tc = generate_wbw_advanced_translation_text_clip(trans_text, is_short, duration, 50)
    
    composite = CompositeVideoClip([bg, ac, tc], size=res).set_duration(duration)
    # Return frame at middle
    return composite.get_frame(duration / 2)

def get_moviepy_interlinear_frame(scene_data):
    is_short = scene_data.get("is_short", False)
    res = get_resolution(is_short)
    duration = (scene_data["end_ms"] - scene_data["start_ms"]) / 1000.0
    
    # 1. Background
    bg = ColorClip(size=res, color=(0,0,0)).set_duration(duration)
    
    # 2. Interlinear clip
    ic = generate_wbw_interlinear_text_clip(
        scene_data["words"], scene_data["translations"],
        is_short, duration, 60, 20
    )
    
    composite = CompositeVideoClip([bg, ic], size=res).set_duration(duration)
    return composite.get_frame(duration / 2)

def test_visual_parity_standard_layout():
    scene_data = {
        "words": ["اللَّهُ"],
        "translations": ["Allah"],
        "start_ms": 0,
        "end_ms": 1000,
        "is_short": False,
        "layout": "standard"
    }
    renderer = WBWFastRenderer(scene_data)
    fast_frame = renderer.get_frame_at(0.5)
    
    # Save for debug
    os.makedirs("debug_test", exist_ok=True)
    Image.fromarray(fast_frame).save("debug_test/fast_standard.png")
    
    moviepy_frame = get_moviepy_standard_frame(scene_data)
    Image.fromarray(moviepy_frame).save("debug_test/moviepy_standard.png")
    
    diff = np.abs(fast_frame.astype(float) - moviepy_frame.astype(float))
    mean_diff = np.mean(diff)
    
    # We want a very low difference for parity. 
    # A mean difference of 5.0 across 2M pixels is actually quite large for text-on-black.
    # Let's try 0.1 as a target for true parity.
    assert mean_diff < 0.1, f"Standard layout mean difference too high: {mean_diff}"

def test_visual_parity_interlinear_layout():
    scene_data = {
        "words": ["اللَّهُ"],
        "translations": ["Allah"],
        "start_ms": 0,
        "end_ms": 1000,
        "is_short": False,
        "layout": "interlinear"
    }
    renderer = WBWFastRenderer(scene_data)
    fast_frame = renderer.get_frame_at(0.5)
    Image.fromarray(fast_frame).save("debug_test/fast_interlinear.png")
    
    moviepy_frame = get_moviepy_interlinear_frame(scene_data)
    Image.fromarray(moviepy_frame).save("debug_test/moviepy_interlinear.png")
    
    diff = np.abs(fast_frame.astype(float) - moviepy_frame.astype(float))
    mean_diff = np.mean(diff)
    
    assert mean_diff < 0.1, f"Interlinear layout mean difference too high: {mean_diff}"
