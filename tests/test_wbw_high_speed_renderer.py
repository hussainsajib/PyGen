import pytest
import numpy as np
from PIL import Image
import os

# We assume the class will be in factories/wbw_fast_render.py
try:
    from factories.wbw_fast_render import WBWFastRenderer
except ImportError:
    # This is expected during the 'Red' phase of TDD
    WBWFastRenderer = None

@pytest.mark.skipif(WBWFastRenderer is None, reason="WBWFastRenderer not implemented yet")
def test_wbw_fast_renderer_initialization():
    # Mock data for a scene
    scene_data = {
        "surah_number": 1,
        "ayah_number": 1,
        "words": ["test", "words"],
        "translations": ["পরীক্ষা", "শব্দ"],
        "start_ms": 0,
        "end_ms": 2000,
        "is_short": True,
        "layout": "standard" # or "interlinear"
    }
    
    renderer = WBWFastRenderer(
        scene_data=scene_data,
        background_path=None, # Should fallback to black or default
        resolution=(1080, 1920)
    )
    
    assert renderer.scene_data == scene_data
    assert renderer.resolution == (1080, 1920)

@pytest.mark.skipif(WBWFastRenderer is None, reason="WBWFastRenderer not implemented yet")
def test_wbw_fast_renderer_frame_generation():
    scene_data = {
        "surah_number": 1,
        "ayah_number": 1,
        "words": ["test"],
        "translations": ["পরীক্ষা"],
        "start_ms": 1000,
        "end_ms": 2000,
        "is_short": True,
        "layout": "standard"
    }
    
    renderer = WBWFastRenderer(
        scene_data=scene_data,
        background_path=None,
        resolution=(1080, 1920)
    )
    
    # Pre-render base image
    renderer.prepare_static_base()
    
    # Frame at 0s (before word starts)
    frame_0 = renderer.get_frame_at(0.0)
    assert isinstance(frame_0, np.ndarray)
    assert frame_0.shape == (1920, 1080, 3) # height, width, RGB
    
    # Frame at 1.5s (during word highlight)
    frame_highlight = renderer.get_frame_at(1.5)
    assert isinstance(frame_highlight, np.ndarray)
    assert frame_highlight.shape == (1920, 1080, 3)
    
    # Frames should be different due to highlight
    assert not np.array_equal(frame_0, frame_highlight)

def test_trigger_red_phase():
    """Explicitly fail if WBWFastRenderer is missing to confirm Red phase."""
    if WBWFastRenderer is None:
        pytest.fail("WBWFastRenderer class is missing! (Expected in Red phase)")
