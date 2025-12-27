import pytest
from unittest.mock import patch, MagicMock
from factories import single_clip

def test_generate_wbw_interlinear_text_clip_exists():
    assert hasattr(single_clip, "generate_wbw_interlinear_text_clip")

@patch("factories.single_clip.TextClip")
@patch("factories.single_clip.ColorClip")
@patch("factories.single_clip.CompositeVideoClip")
def test_generate_wbw_interlinear_text_clip_logic(mock_composite, mock_color, mock_text):
    # Mock sizes
    def text_clip_side_effect(*args, **kwargs):
        m = MagicMock()
        m.w = 50
        m.h = 20
        return m
    mock_text.side_effect = text_clip_side_effect
    
    def color_clip_side_effect(*args, **kwargs):
        m = MagicMock()
        return m
    mock_color.side_effect = color_clip_side_effect
    
    mock_composite.return_value.set_duration.return_value.set_position.return_value = "final_clip"
    
    # Trigger call
    words = ["word1"]
    translations = ["trans1"]
    clip = single_clip.generate_wbw_interlinear_text_clip(
        words, translations, is_short=False, duration=1.0, 
        arabic_font_size=60, translation_font_size=20
    )
    
    # Verify TextClips were created
    assert mock_text.call_count >= 2 # Arabic + Translation
    
    # Verify ColorClip was created (underline)
    assert mock_color.call_count >= 1
    
    # Verify CompositeVideoClip was created
    assert mock_composite.called
    
    # Check return value
    assert clip == "final_clip"