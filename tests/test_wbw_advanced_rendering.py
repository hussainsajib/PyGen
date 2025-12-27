import pytest
from unittest.mock import patch, MagicMock
from processes.surah_video import create_wbw_advanced_ayah_clip
from processes.Classes import Surah, Reciter

@pytest.mark.asyncio
async def test_create_wbw_advanced_ayah_clip_logic():
    # Mocking MoviePy objects to avoid actual rendering
    with patch("processes.surah_video.CompositeVideoClip") as mock_composite:
        with patch("processes.surah_video.AudioFileClip") as mock_audio:
            with patch("processes.surah_video.generate_background") as mock_bg:
                with patch("processes.surah_video.generate_wbw_advanced_arabic_text_clip") as mock_wbw_text:
                    with patch("processes.surah_video.generate_wbw_advanced_translation_text_clip") as mock_wbw_trans:
                        with patch("processes.surah_video.concatenate_videoclips") as mock_concat:
                            with patch("processes.surah_video.get_wbw_text_for_ayah") as mock_get_text:
                                with patch("processes.surah_video.get_wbw_translation_for_ayah") as mock_get_trans:
                                    with patch("processes.surah_video.config_manager.get") as mock_config:
                                        
                                        mock_surah = MagicMock(spec=Surah)
                                        mock_surah.number = 1
                                        mock_reciter = MagicMock(spec=Reciter)
                                        mock_reciter.bangla_name = "টেস্ট"
                                        
                                        mock_full_audio = MagicMock()
                                        mock_full_audio.duration = 10.0
                                        
                                        mock_get_text.return_value = ["word1", "word2"]
                                        mock_get_trans.return_value = ["trans1", "trans2"]
                                        mock_config.side_effect = lambda k, d: "10" if "LIMIT" in k else "40"
                                        
                                        segments = [[1, 0, 1000], [2, 1000, 2000]]
                                        
                                        clip = create_wbw_advanced_ayah_clip(mock_surah, 1, mock_reciter, mock_full_audio, False, segments)
                                        
                                        assert clip is not None
                                        # Verify it attempted to segment and create clips
                                        assert mock_wbw_text.called
                                        assert mock_wbw_trans.called
                                        assert mock_concat.called