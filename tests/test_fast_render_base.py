import pytest
import numpy as np
from PIL import Image
from factories.mushaf_fast_render import MushafRenderer

def test_mushaf_renderer_initialization():
    renderer = MushafRenderer(
        page_number=1,
        is_short=True,
        lines=[], # Empty lines for now
        font_scale=0.8
    )
    assert renderer.page_number == 1
    assert renderer.is_short is True
    assert renderer.resolution == (1080, 1920)

def test_mushaf_renderer_frame_at_timestamp():
    # Mock data for a single line
    lines = [{
        "line_type": "ayah",
        "words": [{"text": "test"}],
        "start_ms": 1000,
        "end_ms": 2000
    }]
    
    renderer = MushafRenderer(
        page_number=1,
        is_short=True,
        lines=lines,
        font_scale=0.8
    )
    
    # Pre-render static base
    renderer.prepare_static_base()
    
    # Frame at 0s (no highlight)
    frame_0 = renderer.get_frame_at(0.0)
    assert isinstance(frame_0, np.ndarray)
    assert frame_0.shape == (1920, 1080, 3) # RGB
    
    # Frame at 1.5s (should have highlight)
    frame_highlight = renderer.get_frame_at(1.5)
    assert isinstance(frame_highlight, np.ndarray)
    
    # Check that frames are different
    assert not np.array_equal(frame_0, frame_highlight)
