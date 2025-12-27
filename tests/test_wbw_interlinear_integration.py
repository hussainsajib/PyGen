import pytest
from unittest.mock import patch, MagicMock
from processes.surah_video import create_wbw_advanced_ayah_clip
from processes.Classes import Surah, Reciter

@pytest.mark.asyncio
async def test_create_wbw_advanced_ayah_clip_integration_interlinear():
    with patch("processes.surah_video.get_wbw_text_for_ayah") as mock_get_text, \
         patch("processes.surah_video.get_wbw_translation_for_ayah") as mock_get_trans, \
         patch("processes.surah_video.generate_wbw_interlinear_text_clip") as mock_gen_interlinear, \
         patch("processes.surah_video.generate_wbw_advanced_arabic_text_clip") as mock_gen_arabic, \
         patch("processes.surah_video.config_manager.get") as mock_get_config, \
         patch("processes.surah_video.CompositeVideoClip") as mock_composite, \
         patch("processes.surah_video.concatenate_videoclips") as mock_concat, \
         patch("processes.surah_video.concatenate_audioclips") as mock_concat_audio, \
         patch("processes.surah_video.make_silence") as mock_silence, \
         patch("processes.surah_video.AudioFileClip") as mock_audio:
        
        # Setup mocks
        mock_surah = MagicMock(spec=Surah)
        mock_surah.number = 1
        mock_reciter = MagicMock(spec=Reciter)
        mock_reciter.bangla_name = "টেস্ট"
        
        mock_get_text.return_value = ["word1"]
        mock_get_trans.return_value = ["trans1"]
        
        # Ensure durations are numbers
        mock_line_clip = MagicMock()
        mock_line_clip.duration = 1.0
        mock_composite.return_value.set_duration.return_value = mock_line_clip
        
        # 1. Test with interlinear ENABLED
        mock_get_config.side_effect = lambda k, d=None: "True" if k == "WBW_INTERLINEAR_ENABLED" else d
        
        segments = [[1, 0, 1000]]
        full_audio = MagicMock()
        full_audio.duration = 10.0
        
        create_wbw_advanced_ayah_clip(mock_surah, 1, mock_reciter, full_audio, False, segments)
        
        # Verify interlinear was called, standard Arabic was NOT called
        assert mock_gen_interlinear.called
        assert not mock_gen_arabic.called
        
        # 2. Test with interlinear DISABLED
        mock_gen_interlinear.reset_mock()
        mock_gen_arabic.reset_mock()
        mock_get_config.side_effect = lambda k, d=None: "False" if k == "WBW_INTERLINEAR_ENABLED" else d
        
        create_wbw_advanced_ayah_clip(mock_surah, 1, mock_reciter, full_audio, False, segments)
        
        # Verify interlinear was NOT called, standard Arabic WAS called
        assert not mock_gen_interlinear.called
        assert mock_gen_arabic.called
