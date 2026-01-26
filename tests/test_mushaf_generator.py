import pytest
from unittest.mock import MagicMock, patch
from factories.single_clip import generate_mushaf_page_clip

def test_generate_mushaf_page_clip_structure():
    """Test that the generator creates a CompositeVideoClip with expected structure."""
    mock_lines = [
        {
            "line_number": 1,
            "line_type": "ayah",
            "words": [{"text": "ﱁ"}],
            "start_ms": 0,
            "end_ms": 1000
        },
        {
            "line_number": 2,
            "line_type": "ayah",
            "words": [{"text": "ﱂ"}],
            "start_ms": 1000,
            "end_ms": 2000
        }
    ]
    
    # Mocking MoviePy components
    with patch("factories.single_clip.TextClip") as mock_text_clip, \
         patch("factories.single_clip.ColorClip") as mock_color_clip, \
         patch("factories.single_clip.CompositeVideoClip") as mock_composite:
        
        # Configure mocks to return another mock
        mock_text_clip.return_value.set_position.return_value.set_duration.return_value = MagicMock()
        mock_color_clip.return_value.set_position.return_value.set_duration.return_value.set_opacity.return_value = MagicMock()
        
        # Adding size to mock_text_clip return value for layout calculations
        mock_text_clip.return_value.w = 400
        mock_text_clip.return_value.h = 50
        
        clip = generate_mushaf_page_clip(mock_lines, page_number=1, is_short=False, duration=2.0)
        
        # Should have called TextClip for each line (2 lines)
        assert mock_text_clip.call_count >= 2
        # Should have called CompositeVideoClip to assemble the page
        mock_composite.assert_called()