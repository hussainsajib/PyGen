import pytest
from unittest.mock import MagicMock, patch
from factories.single_clip import generate_mushaf_page_clip
import numpy as np

def test_generate_mushaf_page_clip_font_selection():
    """Test that correct fonts are selected based on line_type."""
    
    lines = [
        {
            "line_number": 1, 
            "line_type": "basmallah", 
            "words": [],
            "surah_number": 1
        },
        {
            "line_number": 2, 
            "line_type": "surah_name", 
            "words": [], 
            "surah_number": 1
        },
        {
            "line_number": 3, 
            "line_type": "ayah", 
            "words": [{"text": "W1"}, {"text": "W2"}], 
            "surah_number": 1
        }
    ]
    
    # Create a dummy image array (H, W, 4)
    dummy_img = np.zeros((10, 10, 4), dtype=np.uint8)
    # Set some alpha to > 0 so it passes the visibility check by default
    dummy_img[..., 3] = 255
    
    with patch("factories.single_clip.render_mushaf_text_to_image") as mock_render, \
         patch("factories.single_clip.ImageClip") as mock_img_clip, \
         patch("factories.single_clip.CompositeVideoClip") as mock_composite, \
         patch("factories.single_clip.os.path.exists", return_value=True), \
         patch("processes.Classes.surah.Surah") as mock_surah_cls:
         
        # Mock Surah class
        mock_surah_instance = MagicMock()
        mock_surah_instance.arabic_name = "ArabicName"
        mock_surah_cls.return_value = mock_surah_instance
        
        # Mock render return (real numpy array)
        mock_render.return_value = dummy_img
        
        generate_mushaf_page_clip(lines, page_number=5, is_short=False, duration=1.0)
        
        # Check render calls
        # 1. Basmallah
        args_bsml = mock_render.call_args_list[0]
        # Text for basmallah fallback is "بسم الله الرحمن الرحيم" if empty in words
        assert "QCF_BSML.TTF" in args_bsml[0][1] 
        
        # 2. Surah Name
        args_sura = mock_render.call_args_list[1]
        assert "QCF_SurahHeader_COLOR-Regular.ttf" in args_sura[0][1]
        
        # 3. Ayah (Standard Line)
        args_ayah = mock_render.call_args_list[2]
        # Text should be W2W1 (reversed)
        assert args_ayah[0][0] == "W2W1"
        assert "p5.ttf" in args_ayah[0][1]

def test_generate_mushaf_page_clip_surah_fallback():
    """Test fallback logic when Surah font fails to render."""
    lines = [
        {
            "line_number": 1, 
            "line_type": "surah_name", 
            "words": [], 
            "surah_number": 1
        }
    ]
    
    # Dummy empty image (alpha 0)
    empty_img = np.zeros((10, 10, 4), dtype=np.uint8)
    # Dummy visible image
    visible_img = np.zeros((10, 10, 4), dtype=np.uint8)
    visible_img[..., 3] = 255
    
    with patch("factories.single_clip.render_mushaf_text_to_image") as mock_render, \
         patch("factories.single_clip.ImageClip") as mock_img_clip, \
         patch("factories.single_clip.CompositeVideoClip"), \
         patch("factories.single_clip.os.path.exists", return_value=True), \
         patch("processes.Classes.surah.Surah"):
         
        # Side effect: first call returns empty, second returns visible
        mock_render.side_effect = [empty_img, visible_img]
        
        generate_mushaf_page_clip(lines, page_number=5, is_short=False, duration=1.0)
        
        assert mock_render.call_count == 2
        args_first = mock_render.call_args_list[0]
        args_second = mock_render.call_args_list[1]
        
        assert "QCF_SurahHeader_COLOR-Regular.ttf" in args_first[0][1]
        assert "arial.ttf" in args_second[0][1]
