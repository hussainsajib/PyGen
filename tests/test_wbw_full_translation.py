import pytest
from unittest.mock import patch, MagicMock
from processes.surah_video import create_wbw_advanced_ayah_clip
from processes.Classes import Surah, Reciter

@pytest.mark.asyncio
async def test_create_wbw_full_translation_enabled():
    with patch("processes.surah_video.CompositeVideoClip") as mock_composite, \
         patch("processes.surah_video.AudioFileClip") as mock_audio, \
         patch("processes.surah_video.generate_background") as mock_bg, \
         patch("processes.surah_video.generate_wbw_advanced_arabic_text_clip") as mock_wbw_text, \
         patch("processes.surah_video.generate_wbw_advanced_translation_text_clip") as mock_wbw_trans, \
         patch("processes.surah_video.concatenate_videoclips") as mock_concat, \
         patch("processes.surah_video.concatenate_audioclips") as mock_audio_concat, \
         patch("db_ops.crud_wbw.get_wbw_text_for_ayah") as mock_get_text, \
         patch("db_ops.crud_wbw.get_wbw_translation_for_ayah") as mock_get_trans, \
         patch("processes.surah_video.config_manager.get") as mock_get_config, \
         patch("processes.surah_video.get_full_translation_for_ayah") as mock_get_full_trans, \
         patch("processes.surah_video.generate_full_ayah_translation_clip") as mock_gen_full_trans_clip:
            
        mock_final_clip = MagicMock()
        mock_final_clip.duration = 1.0
        mock_concat.return_value = mock_final_clip
        
        mock_audio_concat.return_value = MagicMock()
        mock_audio_concat.return_value.duration = 1.0

        mock_surah = MagicMock(spec=Surah)
        mock_surah.number = 1
        mock_reciter = MagicMock(spec=Reciter)
        mock_reciter.bangla_name = "Reciter"
        
        mock_full_audio = MagicMock()
        mock_full_audio.duration = 10.0
        
        mock_get_text.return_value = ["word"]
        mock_get_trans.return_value = ["trans"]
        
        # Config mocks
        def config_side_effect(key, default=None):
            if key == "WBW_FULL_TRANSLATION_ENABLED": return "True"
            if key == "WBW_FULL_TRANSLATION_SOURCE": return "rawai_al_bayan"
            if key == "WBW_DELAY_BETWEEN_AYAH": return "0"
            if key == "WBW_INTERLINEAR_ENABLED": return "False"
            return default
            
        mock_get_config.side_effect = config_side_effect
        
        segments = [[1, 0, 1000]]
        
        create_wbw_advanced_ayah_clip(mock_surah, 1, mock_reciter, mock_full_audio, False, segments)
        
        # Verify full translation was fetched
        mock_get_full_trans.assert_called_once()
        # Verify text clip generation was called
        mock_gen_full_trans_clip.assert_called()
