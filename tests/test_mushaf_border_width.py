import pytest
from unittest.mock import patch, MagicMock
from factories.single_clip import calculate_mushaf_border_width, generate_mushaf_page_clip

def test_calculate_mushaf_border_width():
    """Test the logic for calculating border width based on percentage."""
    assert calculate_mushaf_border_width(1000, 50) == 500
    assert calculate_mushaf_border_width(1000, 40) == 400
    assert calculate_mushaf_border_width(100, 10) == 10
    assert calculate_mushaf_border_width(1920, 20) == 384

@patch("factories.single_clip.CompositeVideoClip")
@patch("factories.single_clip.config_manager")
@patch("factories.single_clip.generate_mushaf_border_clip")
@patch("factories.single_clip.generate_background")
@patch("factories.single_clip.get_resolution")
def test_generate_mushaf_page_clip_uses_config(mock_resolution, mock_bg, mock_border, mock_config, mock_composite):
    """Test that generate_mushaf_page_clip reads the config and applies the width."""
    # Setup mocks
    def config_side_effect(key, default=None):
        if key == "MUSHAF_BORDER_WIDTH_PERCENT":
            return "30"
        return default
    mock_config.get.side_effect = config_side_effect
    
    mock_resolution.return_value = (1000, 2000)

    # Mock border clip return
    mock_border_clip = MagicMock()
    mock_border_clip.set_position.return_value = mock_border_clip
    mock_border.return_value = mock_border_clip
    
    # Mock background
    mock_bg_clip = MagicMock()
    mock_bg.return_value = mock_bg_clip

    # Call function
    lines = []
    page_number = 1
    is_short = False
    duration = 5.0
    
    generate_mushaf_page_clip(lines, page_number, is_short, duration)
        
    # Verify generate_mushaf_border_clip was called with expected width
    # Expected width: 1000 * 0.30 = 300
    
    args, kwargs = mock_border.call_args
    assert kwargs['size'][0] == 300 

@patch("factories.single_clip.CompositeVideoClip")
@patch("factories.single_clip.config_manager")
@patch("factories.single_clip.generate_mushaf_border_clip")
@patch("factories.single_clip.generate_background")
@patch("factories.single_clip.get_resolution")
def test_generate_mushaf_page_clip_default_config(mock_resolution, mock_bg, mock_border, mock_config, mock_composite):
    """Test that generate_mushaf_page_clip uses default 40% if config fails or missing."""
    # Setup mocks
    mock_config.get.return_value = "invalid"
    
    mock_resolution.return_value = (1000, 2000)

    # Mock border clip return
    mock_border_clip = MagicMock()
    mock_border_clip.set_position.return_value = mock_border_clip
    mock_border.return_value = mock_border_clip
    
    # Mock background
    mock_bg_clip = MagicMock()
    mock_bg.return_value = mock_bg_clip

    # Call function
    lines = []
    page_number = 1
    is_short = False
    duration = 5.0
    
    generate_mushaf_page_clip(lines, page_number, is_short, duration)
        
    # Verify fallback to 40%
    # Expected width: 1000 * 0.40 = 400
    
    args, kwargs = mock_border.call_args
    assert kwargs['size'][0] == 400