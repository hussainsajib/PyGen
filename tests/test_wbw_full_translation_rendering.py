import pytest
from unittest.mock import patch, MagicMock
from processes.surah_video import create_ayah_clip, create_wbw_ayah_clip, create_wbw_advanced_ayah_clip
from processes.Classes import Surah, Reciter

@pytest.fixture
def mock_context():
    with (patch("processes.surah_video.CompositeVideoClip") as mock_composite,
         patch("processes.surah_video.AudioFileClip") as mock_audio,
         patch("processes.surah_video.generate_background") as mock_bg,
         patch("processes.surah_video.generate_arabic_text_clip") as mock_arabic,
         patch("processes.surah_video.generate_translation_text_clip") as mock_trans,
         patch("processes.surah_video.generate_wbw_arabic_text_clip") as mock_wbw_arabic,
         patch("processes.surah_video.generate_wbw_advanced_arabic_text_clip") as mock_adv_arabic,
         patch("processes.surah_video.generate_wbw_advanced_translation_text_clip") as mock_adv_trans,
         patch("processes.surah_video.generate_wbw_interlinear_text_clip") as mock_interlinear,
         patch("processes.surah_video.generate_full_ayah_translation_clip") as mock_full_trans_clip,
         patch("processes.surah_video.get_full_translation_for_ayah") as mock_get_full_trans,
         patch("processes.surah_video.config_manager") as mock_config,
         patch("processes.surah_video.get_resolution") as mock_res,
         patch("processes.surah_video.concatenate_videoclips") as mock_concat,
         patch("processes.surah_video.concatenate_audioclips") as mock_audio_concat,
         patch("processes.surah_video.generate_reciter_name_clip") as mock_reciter_clip,
         patch("processes.surah_video.generate_surah_info_clip") as mock_surah_clip,
         patch("processes.surah_video.generate_brand_clip") as mock_brand_clip,
         patch("db_ops.crud_wbw.get_wbw_text_for_ayah") as mock_get_wbw_text,
         patch("db_ops.crud_wbw.get_wbw_translation_for_ayah") as mock_get_wbw_trans):
            
        mock_res.return_value = (1920, 1080)
        mock_get_full_trans.return_value = "Full Ayah Translation"
        
        # Default config mocks
        def config_get_side_effect(key, default=None):
            if key == "WBW_FULL_TRANSLATION_ENABLED": return "True"
            if key == "WBW_FULL_TRANSLATION_SOURCE": return "rawai_al_bayan"
            if key == "WBW_DELAY_BETWEEN_AYAH": return "0"
            if key == "WBW_INTERLINEAR_ENABLED": return "False"
            return default
        mock_config.get.side_effect = config_get_side_effect
        
        # Return a mock clip from all generation functions
        mock_clip = MagicMock()
        mock_clip.set_position.return_value = mock_clip
        mock_clip.set_duration.return_value = mock_clip
        mock_clip.set_audio.return_value = mock_clip
        
        mock_bg.return_value = mock_clip
        mock_arabic.return_value = mock_clip
        mock_trans.return_value = mock_clip
        mock_wbw_arabic.return_value = mock_clip
        mock_adv_arabic.return_value = mock_clip
        mock_adv_trans.return_value = mock_clip
        mock_interlinear.return_value = mock_clip
        mock_full_trans_clip.return_value = mock_clip
        mock_reciter_clip.return_value = mock_clip
        mock_surah_clip.return_value = mock_clip
        mock_brand_clip.return_value = mock_clip
        
        mock_composite.return_value = mock_clip
        
        yield {
            "mock_full_trans_clip": mock_full_trans_clip,
            "mock_get_full_trans": mock_get_full_trans,
            "mock_concat": mock_concat
        }

@pytest.mark.asyncio
async def test_create_ayah_clip_full_translation(mock_context):
    surah = MagicMock(spec=Surah)
    surah.number = 1
    ayah = 1
    reciter = MagicMock(spec=Reciter)
    reciter.bangla_name = "Reciter Bangla"
    reciter.english_name = "Reciter English"
    
    full_audio = MagicMock()
    full_audio.duration = 10.0
    full_audio.subclip.return_value = MagicMock()
    
    surah_data = {1: {1: {1: "Word"}}}
    translation_data = {(1, 1): "Translation"}
    
    create_ayah_clip(surah, ayah, reciter, 0, 5000, surah_data, translation_data, full_audio, False)
    
    mock_context["mock_full_trans_clip"].assert_called_once()

@pytest.mark.asyncio
async def test_create_wbw_ayah_clip_full_translation(mock_context):
    surah = MagicMock(spec=Surah)
    surah.number = 1
    ayah = 1
    reciter = MagicMock(spec=Reciter)
    reciter.bangla_name = "Reciter Bangla"
    reciter.english_name = "Reciter English"
    
    full_audio = MagicMock()
    full_audio.duration = 10.0
    full_audio.subclip.return_value = MagicMock()
    
    surah_data = {1: {1: {1: "Word"}}}
    translation_data = {(1, 1): "Translation"}
    segments = [[1, 0, 5000]]
    
    create_wbw_ayah_clip(surah, ayah, reciter, 0, 5000, surah_data, translation_data, full_audio, False, segments)
    
    mock_context["mock_full_trans_clip"].assert_called_once()

@pytest.mark.asyncio
async def test_create_wbw_advanced_ayah_clip_full_translation(mock_context):
    surah = MagicMock(spec=Surah)
    surah.number = 1
    ayah = 1
    reciter = MagicMock(spec=Reciter)
    reciter.bangla_name = "Reciter Bangla"
    reciter.english_name = "Reciter English"
    
    full_audio = MagicMock()
    full_audio.duration = 10.0
    full_audio.subclip.return_value = MagicMock()
    
    segments = [[1, 0, 5000]]
    
    mock_final_clip = MagicMock()
    mock_final_clip.duration = 5.0
    mock_context["mock_concat"].return_value = mock_final_clip

    create_wbw_advanced_ayah_clip(surah, ayah, reciter, full_audio, False, segments)
    
    mock_context["mock_full_trans_clip"].assert_called()
