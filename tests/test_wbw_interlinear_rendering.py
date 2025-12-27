import pytest
from unittest.mock import patch, MagicMock
from factories import single_clip

def test_generate_wbw_interlinear_text_clip_exists():
    # This will fail until implemented
    assert hasattr(single_clip, "generate_wbw_interlinear_text_clip")

@patch("factories.single_clip.ImageClip")
@patch("factories.single_clip.Image")
@patch("factories.single_clip.ImageDraw")
@patch("factories.single_clip.ImageFont")
def test_generate_wbw_interlinear_text_clip_logic(mock_font, mock_draw, mock_image, mock_image_clip):
    # Mock font metrics
    mock_font_instance = MagicMock()
    mock_font.truetype.return_value = mock_font_instance
    mock_font_instance.getbbox.return_value = (0, 0, 100, 50) # width 100, height 50
    
    # Mock image creation
    mock_img_instance = MagicMock()
    mock_image.new.return_value = mock_img_instance
    
    # Trigger call
    words = ["word1"]
    translations = ["trans1"]
    clip = single_clip.generate_wbw_interlinear_text_clip(
        words, translations, is_short=False, duration=1.0, 
        arabic_font_size=60, translation_font_size=20
    )
    
    # Verify Pillow was used to draw
    assert mock_image.new.called
    assert mock_draw.Draw.called
    
    # Check if Draw.text was called for both arabic and translation
    draw_instance = mock_draw.Draw.return_value
    assert draw_instance.text.call_count >= 2
    
    # Check if line (underline) was drawn
    assert draw_instance.line.called
