import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from processes.surah_video import create_wbw_advanced_ayah_clip
from processes.Classes import Surah, Reciter

@pytest.mark.asyncio
async def test_create_wbw_advanced_ayah_clip_language_path():
    # Setup mocks
    mock_surah = MagicMock(spec=Surah)
    mock_surah.number = 1
    mock_reciter = MagicMock(spec=Reciter)
    mock_reciter.bangla_name = "টেস্ট"
    
    mock_audio = MagicMock()
    mock_audio.duration = 10.0
    
    segments = [[1, 0, 1000]]
    
    with patch("processes.surah_video.config_manager") as mock_config, \
         patch("processes.surah_video.get_wbw_text_for_ayah") as mock_get_text, \
         patch("processes.surah_video.get_wbw_translation_for_ayah") as mock_get_trans, \
         patch("processes.surah_video.get_full_translation_for_ayah"), \
         patch("processes.surah_video.generate_background"), \
         patch("processes.surah_video.generate_wbw_advanced_arabic_text_clip"), \
         patch("processes.surah_video.generate_wbw_advanced_translation_text_clip"), \
         patch("processes.surah_video.generate_wbw_interlinear_text_clip"), \
         patch("processes.surah_video.generate_full_ayah_translation_clip"), \
         patch("processes.surah_video.generate_reciter_name_clip"), \
         patch("processes.surah_video.generate_surah_info_clip"), \
         patch("processes.surah_video.generate_brand_clip"), \
         patch("processes.surah_video.CompositeVideoClip") as mock_composite, \
         patch("processes.surah_video.concatenate_videoclips"), \
         patch("processes.surah_video.concatenate_audioclips"), \
         patch("processes.surah_video.make_silence"), \
         patch("processes.surah_video.AudioFileClip"):
        
        # Ensure durations are numbers
        mock_line_clip = MagicMock()
        mock_line_clip.duration = 1.0
        mock_composite.return_value.set_duration.return_value = mock_line_clip

        # 1. Test Bengali
        mock_config.get.side_effect = lambda k, d=None: "bengali" if k == "DEFAULT_LANGUAGE" else d
        mock_get_text.return_value = ["word"]
        mock_get_trans.return_value = ["trans"]
        
        create_wbw_advanced_ayah_clip(mock_surah, 1, mock_reciter, mock_audio, False, segments)
        
        expected_bengali_db = "databases/translation/bengali/bangali-word-by-word-translation.sqlite"
        mock_get_trans.assert_called_with(expected_bengali_db, 1, 1)
        
        # 2. Test English
        mock_get_trans.reset_mock()
        mock_config.get.side_effect = lambda k, d=None: "english" if k == "DEFAULT_LANGUAGE" else d
        
        create_wbw_advanced_ayah_clip(mock_surah, 1, mock_reciter, mock_audio, False, segments)
        
        expected_english_db = "databases/translation/english/word-by-word-translation.sqlite"
        mock_get_trans.assert_called_with(expected_english_db, 1, 1)
