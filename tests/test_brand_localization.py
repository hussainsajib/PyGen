import pytest
from unittest.mock import patch, MagicMock
from factories.single_clip import generate_brand_clip

def test_generate_brand_clip_hardcoded_brand_name():
    with patch("factories.single_clip.FOOTER_CONFIG", {"fontsize": 30, "color": "white"}), \
         patch("factories.single_clip.COMMON", {
             "f_channel_info_position": lambda is_short, clip_width: (0,0)
         }), \
         patch("factories.single_clip.TextClip") as mock_text_clip_cls: # Mock the class
        
        # Configure the mock TextClip class to return a mock instance
        mock_text_clip_instance = MagicMock()
        mock_text_clip_instance.set_position.return_value = mock_text_clip_instance
        mock_text_clip_instance.set_duration.return_value = mock_text_clip_instance
        mock_text_clip_cls.return_value = mock_text_clip_instance
        
        # Call the function under test
        generate_brand_clip("তাকওয়া বাংলা", is_short=False, duration=1)
        
        # Assert that TextClip was called with the correct text
        mock_text_clip_cls.assert_called_once()
        args, kwargs = mock_text_clip_cls.call_args
        assert args[0] == "তাকওয়া বাংলা"
