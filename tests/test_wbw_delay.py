import pytest
from unittest.mock import patch, MagicMock
from processes.surah_video import create_wbw_advanced_ayah_clip
from processes.Classes import Surah, Reciter

@pytest.mark.asyncio
async def test_create_wbw_advanced_ayah_clip_duration_with_delay():
    with patch("processes.surah_video.CompositeVideoClip") as mock_composite:
        with patch("processes.surah_video.AudioFileClip") as mock_audio:
            with patch("processes.surah_video.generate_background") as mock_bg:
                with patch("processes.surah_video.generate_wbw_advanced_arabic_text_clip") as mock_wbw_text:
                    with patch("processes.surah_video.generate_wbw_advanced_translation_text_clip") as mock_wbw_trans:
                        with patch("processes.surah_video.concatenate_audioclips") as mock_audio_concat:
                            # Mock concatenate_videoclips to return a mock clip with set_duration/set_audio
                            mock_final_clip = MagicMock()
                            mock_final_clip.duration = 1.0 # Default
                            
                            # Mock audio concat return value
                            mock_audio_concat.return_value = MagicMock()
                            mock_audio_concat.return_value.duration = 1.0

                            # Mocking concatenate_videoclips to actually sum durations or similar is complex
                            # Let's mock it to return a MagicMock that we can check
                            with patch("processes.surah_video.concatenate_videoclips", return_value=mock_final_clip) as mock_concat:
                                with patch("db_ops.crud_wbw.get_wbw_text_for_ayah") as mock_get_text:
                                    with patch("db_ops.crud_wbw.get_wbw_translation_for_ayah") as mock_get_trans:
                                        with patch("processes.surah_video.config_manager.get") as mock_get_config:
                                            
                                            mock_surah = MagicMock(spec=Surah)
                                            mock_surah.number = 1
                                            mock_reciter = MagicMock(spec=Reciter)
                                            mock_reciter.bangla_name = "টেস্ট"
                                            
                                            mock_full_audio = MagicMock()
                                            mock_full_audio.duration = 10.0
                                            
                                            mock_get_text.return_value = ["word1"]
                                            mock_get_trans.return_value = ["trans1"]
                                            
                                            # Return 0.5 for delay
                                            mock_get_config.side_effect = lambda k, d=None: "0.5" if k == "WBW_DELAY_BETWEEN_AYAH" else d
                                            
                                            segments = [[1, 0, 1000]] # 1 second
                                            
                                            # Trigger call
                                            create_wbw_advanced_ayah_clip(mock_surah, 1, mock_reciter, mock_full_audio, False, segments)
                                            
                                            # Check if it fetched the delay config
                                            # (This will fail if logic not implemented)
                                            mock_get_config.assert_any_call("WBW_DELAY_BETWEEN_AYAH", 0.5)
