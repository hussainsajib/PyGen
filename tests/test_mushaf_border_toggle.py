import pytest
from unittest.mock import patch, MagicMock
from factories.single_clip import generate_mushaf_page_clip

@patch("factories.single_clip.CompositeVideoClip")
@patch("factories.single_clip.config_manager")
@patch("factories.single_clip.generate_mushaf_border_clip")
@patch("factories.single_clip.generate_background")
@patch("factories.single_clip.get_resolution")
def test_generate_mushaf_page_clip_border_enabled(mock_resolution, mock_bg, mock_border, mock_config, mock_composite):
    """Test that border is rendered when MUSHAF_BORDER_ENABLED is True."""
    # Setup mocks
    def config_side_effect(key, default=None):
        if key == "MUSHAF_BORDER_ENABLED":
            return "True"
        if key == "MUSHAF_BORDER_WIDTH_PERCENT":
            return "40"
        return default
    mock_config.get.side_effect = config_side_effect
    
    mock_resolution.return_value = (1080, 1920)
    mock_bg.return_value = MagicMock()
    
    mock_border_clip = MagicMock()
    mock_border_clip.set_position.return_value = mock_border_clip
    mock_border.return_value = mock_border_clip

    # Call function
    generate_mushaf_page_clip([], 1, True, 5.0)
    
    # Verify border was generated
    assert mock_border.called

@patch("factories.single_clip.CompositeVideoClip")
@patch("factories.single_clip.config_manager")
@patch("factories.single_clip.generate_mushaf_border_clip")
@patch("factories.single_clip.generate_background")
@patch("factories.single_clip.get_resolution")
def test_generate_mushaf_page_clip_border_disabled(mock_resolution, mock_bg, mock_border, mock_config, mock_composite):
    """Test that border is NOT rendered when MUSHAF_BORDER_ENABLED is False."""
    # Setup mocks
    def config_side_effect(key, default=None):
        if key == "MUSHAF_BORDER_ENABLED":
            return "False"
        if key == "MUSHAF_BORDER_WIDTH_PERCENT":
            return "40"
        return default
    mock_config.get.side_effect = config_side_effect
    
    mock_resolution.return_value = (1080, 1920)
    mock_bg.return_value = MagicMock()

    # Call function
    generate_mushaf_page_clip([], 1, True, 5.0)
    
    # Verify border was NOT generated
    assert not mock_border.called

@patch("factories.single_clip.CompositeVideoClip")
@patch("factories.single_clip.config_manager")
@patch("factories.single_clip.generate_mushaf_border_clip")
@patch("factories.single_clip.generate_background")
@patch("factories.single_clip.get_resolution")
def test_generate_mushaf_page_clip_border_default_disabled(mock_resolution, mock_bg, mock_border, mock_config, mock_composite):
    """Test that border is NOT rendered by default (if config missing)."""
    # Setup mocks
    def config_side_effect(key, default=None):
        if key == "MUSHAF_BORDER_ENABLED":
            return default # Should return "False" from the call site's default
        return default
    mock_config.get.side_effect = config_side_effect
    
    mock_resolution.return_value = (1080, 1920)
    mock_bg.return_value = MagicMock()

    # Call function
    generate_mushaf_page_clip([], 1, True, 5.0)
    
    # Verify border was NOT generated
    assert not mock_border.called
