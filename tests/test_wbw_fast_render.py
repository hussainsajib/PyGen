import pytest
import numpy as np
import os
from PIL import Image
from factories.wbw_fast_render import WBWFastRenderer

def test_renderer_initialization():
    scene_data = {
        "words": ["Word1", "Word2"],
        "translations": ["Trans1", "Trans2"],
        "start_ms": 0,
        "end_ms": 2000,
        "is_short": False
    }
    renderer = WBWFastRenderer(scene_data)
    # Standard resolution is 1920x1080 (width, height)
    assert renderer.width == 1920
    assert renderer.height == 1080
    assert renderer.is_short is False

def test_renderer_get_frame_shape():
    scene_data = {
        "words": ["Word1"],
        "translations": ["Trans1"],
        "start_ms": 0,
        "end_ms": 1000,
        "is_short": True
    }
    renderer = WBWFastRenderer(scene_data)
    frame = renderer.get_frame_at(0.5)
    assert isinstance(frame, np.ndarray)
    # For short, resolution is (1080, 1920) (width, height)
    # Numpy shape is (height, width, 3)
    assert frame.shape == (1920, 1080, 3)

def test_renderer_frame_changes_with_highlight():
    scene_data = {
        "words": ["Word1"],
        "translations": ["Trans1"],
        "start_ms": 0,
        "end_ms": 1000,
        "is_short": False
    }
    renderer = WBWFastRenderer(scene_data)
    # Get frame before start
    frame_before = renderer.get_frame_at(-1.0)
    # Get frame during word
    frame_during = renderer.get_frame_at(0.5)
    
    # These should be different if highlight is applied
    assert not np.array_equal(frame_before, frame_during)

def test_renderer_second_word_highlight_fails_in_skeleton():
    """
    This test is expected to fail with the current skeleton 
    because it only supports a single dummy highlight for index 0.
    """
    scene_data = {
        "words": ["Word1", "Word2"],
        "translations": ["Trans1", "Trans2"],
        "start_ms": 0,
        "end_ms": 2000,
        "word_segments": [
            {"start_ms": 0, "end_ms": 1000},
            {"start_ms": 1000, "end_ms": 2000}
        ],
        "is_short": False
    }
    # We need to enhance get_frame_at to use word_segments for this to pass
    renderer = WBWFastRenderer(scene_data)
    
    # Frame for first word
    frame1 = renderer.get_frame_at(0.5)
    # Frame for second word
    frame2 = renderer.get_frame_at(1.5)
    
    # In the skeleton, frame2 will likely be the same as the base frame (index -1)
    # or it might also be frame1 if active_idx is 0 for the whole scene_data start/end.
    # But wait, the skeleton has:
    # if start_ms <= timestamp_ms <= end_ms: active_idx = 0
    # So for 0.5 and 1.5, active_idx will be 0.
    # Thus frame1 and frame2 will be identical.
    # We want them to be different.
    assert not np.array_equal(frame1, frame2), "Frames for different words should be different"

def test_renderer_static_background():
    # Create a temporary red image
    bg_path = "test_bg.png"
    Image.new('RGB', (1920, 1080), color='red').save(bg_path)
    
    scene_data = {
        "words": ["Word1"],
        "translations": ["Trans1"],
        "start_ms": 0,
        "end_ms": 1000,
        "is_short": False
    }
    try:
        renderer = WBWFastRenderer(scene_data, background_path=bg_path)
        frame = renderer.get_frame_at(0.5)
        # The frame should have a lot of red (unless text/dimming covers it)
        # Standard dimming is 0.3, so it should be dimmed red.
        # [height, width, channel]
        assert frame[0, 0, 0] > 100 # Red channel should be significant
    finally:
        if os.path.exists(bg_path):
            os.remove(bg_path)
