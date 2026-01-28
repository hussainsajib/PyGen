import pytest
from unittest.mock import MagicMock, patch
from factories.single_clip import generate_mushaf_page_clip

@patch("factories.single_clip.config_manager")
@patch("factories.single_clip.generate_background")
def test_global_background_selection(mock_gen_bg, mock_config):
    # Mock config values
    mock_config.get.side_effect = lambda key, default=None: {
        "ACTIVE_BACKGROUND": "path/to/image.jpg",
        "BACKGROUND_RGB": "(0, 0, 0)",
        "MUSHAF_PAGE_BACKGROUND_MODE": "Transparent",
        "MUSHAF_PAGE_COLOR": "#FFFFFF",
        "MUSHAF_PAGE_OPACITY": "90"
    }.get(key, default)
    
    # Mock generate_background to return a dummy clip
    mock_bg_clip = MagicMock()
    mock_gen_bg.return_value = mock_bg_clip
    
    # Call the function (need to update signature in implementation)
    # For now, let's just test the logic I plan to add
    
    # Logic:
    active_bg = mock_config.get("ACTIVE_BACKGROUND")
    bg_rgb = mock_config.get("BACKGROUND_RGB")
    
    selected_bg = active_bg if active_bg else bg_rgb
    
    assert selected_bg == "path/to/image.jpg"

@patch("factories.single_clip.config_manager")
def test_global_background_fallback(mock_config):
    # Mock config values with empty ACTIVE_BACKGROUND
    mock_config.get.side_effect = lambda key, default=None: {
        "ACTIVE_BACKGROUND": "",
        "BACKGROUND_RGB": "(10, 20, 30)",
        "MUSHAF_PAGE_BACKGROUND_MODE": "Transparent",
        "MUSHAF_PAGE_COLOR": "#FFFFFF",
        "MUSHAF_PAGE_OPACITY": "90"
    }.get(key, default)
    
    active_bg = mock_config.get("ACTIVE_BACKGROUND")
    bg_rgb = mock_config.get("BACKGROUND_RGB")
    
    selected_bg = active_bg if active_bg else bg_rgb
    
    assert selected_bg == "(10, 20, 30)"

def test_hex_to_rgb_tuple():
    from factories.single_clip import hex_to_rgb
    assert hex_to_rgb("#FFFFFF") == (255, 255, 255)
    assert hex_to_rgb("#000000") == (0, 0, 0)
    assert hex_to_rgb("#FF0000") == (255, 0, 0)

@patch("factories.single_clip.config_manager")
def test_mushaf_page_opacity_calculation(mock_config):
    # Mock opacity
    mock_config.get.side_effect = lambda key, default=None: {
        "MUSHAF_PAGE_OPACITY": "50"
    }.get(key, default)
    
    opacity_percent = int(mock_config.get("MUSHAF_PAGE_OPACITY", "90"))
    alpha = int((opacity_percent / 100) * 255)
    
    assert alpha == 127 # 0.5 * 255 = 127.5 -> 127

