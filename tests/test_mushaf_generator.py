from unittest.mock import patch, MagicMock
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
    
    # Mocking MoviePy components and the new Pillow renderer
    import numpy as np
    with patch("factories.single_clip.ImageClip") as mock_image_clip, \
         patch("factories.single_clip.ColorClip") as mock_color_clip, \
         patch("factories.single_clip.CompositeVideoClip") as mock_composite, \
         patch("factories.single_clip.render_mushaf_text_to_image") as mock_render:

        # Configure mocks
        mock_render.return_value = np.zeros((100, 100, 4), dtype=np.uint8) # Mock numpy array
        mock_image_clip.return_value.set_position.return_value.set_duration.return_value = MagicMock()
        mock_color_clip.return_value.set_opacity.return_value.set_start.return_value.set_duration.return_value.set_position.return_value = MagicMock()
        
        clip = generate_mushaf_page_clip(mock_lines, page_number=1, is_short=False, duration=2.0)
        
        assert clip is not None
        assert mock_composite.called
        assert mock_render.called
