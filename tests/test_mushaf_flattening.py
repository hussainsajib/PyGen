import pytest
from PIL import Image
from factories.single_clip import pre_render_static_page

def test_pre_render_static_page_output():
    """Verifies that pre_render_static_page returns a valid RGBA image."""
    resolution = (1080, 1920)
    lines = [{
        "line_number": 1,
        "line_type": "surah_name",
        "surah_number": 1,
        "words": []
    }]
    line_positions = [100.0]
    line_height = 50.0
    font_paths = {
        "page": "Arial",
        "bsml": "Arial",
        "sura": "Arial"
    }
    
    img = pre_render_static_page(
        resolution=resolution,
        background_input=None,
        renderable_lines=lines,
        line_positions=line_positions,
        line_height=line_height,
        font_paths=font_paths,
        font_scale=0.8
    )
    
    assert isinstance(img, Image.Image)
    assert img.size == resolution
    assert img.mode == 'RGBA'
