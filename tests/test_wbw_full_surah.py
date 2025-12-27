import pytest
from unittest.mock import patch, MagicMock
from processes.surah_video import generate_surah
from processes.Classes import Surah, Reciter

@pytest.mark.asyncio
async def test_generate_surah_includes_delays():
    # Mocking MoviePy and other dependencies
    with patch("processes.surah_video.AudioFileClip") as mock_audio_clip:
        with patch("processes.surah_video.download_mp3_temp") as mock_download:
            with patch("processes.surah_video.read_surah_data") as mock_surah_data:
                with patch("processes.surah_video.read_text_data") as mock_text_data:
                    with patch("processes.surah_video.read_translation") as mock_trans_data:
                        with patch("processes.surah_video.read_timestamp_data") as mock_ts_data:
                            with patch("processes.surah_video.anyio.from_thread.run") as mock_anyio:
                                with patch("processes.surah_video.get_wbw_timestamps") as mock_wbw_ts:
                                    with patch("processes.surah_video.concatenate_videoclips") as mock_concat:
                                        with patch("processes.surah_video.create_wbw_advanced_ayah_clip") as mock_create_wbw:
                                            with patch("processes.surah_video.config_manager.get") as mock_get_config:
                                                
                                                mock_reciter = MagicMock()
                                                mock_reciter.wbw_database = "test.db"
                                                mock_anyio.return_value = mock_reciter
                                                
                                                # Two ayahs
                                                mock_ts_data.return_value = [
                                                    [1, 1, 0, 1000, "seg1"],
                                                    [1, 2, 1000, 2000, "seg2"]
                                                ]
                                                
                                                mock_wbw_ts.return_value = {
                                                    1: [[1, 0, 1000]],
                                                    2: [[1, 1000, 2000]]
                                                }
                                                
                                                # Return 0.5s delay
                                                mock_get_config.side_effect = lambda k, d=None: "0.5" if k == "WBW_DELAY_BETWEEN_AYAH" else d
                                                
                                                # Mock clips
                                                mock_create_wbw.return_value = MagicMock()
                                                
                                                # Mock concatenate_videoclips to return a final clip
                                                mock_final_video = MagicMock()
                                                mock_concat.return_value = mock_final_video
                                                
                                                # We don't want write_videofile to run
                                                
                                                # Call generate_surah (it will mock everything)
                                                # We might need to mock more things like generate_intro etc.
                                                with patch("processes.surah_video.generate_intro"):
                                                    with patch("processes.surah_video.generate_outro"):
                                                        with patch("processes.surah_video.generate_details"):
                                                            generate_surah(1, "ar.alafasy")
                                                
                                                # Check if mock_create_wbw was called for both ayahs
                                                assert mock_create_wbw.call_count == 2
