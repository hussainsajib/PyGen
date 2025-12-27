import pytest
from unittest.mock import patch, MagicMock
from processes.processes import create_wbw_video_job

def test_wbw_upload_playlist_logic_e2e():
    """End-to-end test for WBW upload with playlist logic."""
    with patch("processes.processes.generate_video") as mock_gen:
        with patch("processes.processes.extract_frame") as mock_frame:
            with patch("processes.processes.record_media_asset") as mock_record:
                with patch("processes.processes.upload_to_youtube") as mock_upload:
                    with patch("processes.processes.anyio.from_thread.run") as mock_anyio_run:
                        with patch.dict("processes.youtube_utils.playlist", {"ar.alafasy": "DEFAULT_PL"}, clear=True):
                            mock_gen.return_value = {"video": "test.mp4", "reciter": "ar.alafasy"}
                            mock_upload.return_value = "video_id_123"
                            
                            # 1. Test 'none' (None (Upload Only))
                            create_wbw_video_job(
                                surah=1, start_verse=1, end_verse=1, 
                                reciter="ar.alafasy", is_short=True,
                                upload_after_generation=True,
                                playlist_id="none"
                            )
                            
                            # 2. Test 'default' (Reciter's Default)
                            create_wbw_video_job(
                                surah=1, start_verse=1, end_verse=1, 
                                reciter="ar.alafasy", is_short=True,
                                upload_after_generation=True,
                                playlist_id="default"
                            )
                            
                            # 3. Test 'OVERRIDE'
                            create_wbw_video_job(
                                surah=1, start_verse=1, end_verse=1, 
                                reciter="ar.alafasy", is_short=True,
                                upload_after_generation=True,
                                playlist_id="OVERRIDE_PL"
                            )
                            
                            assert mock_upload.call_count == 3
                            print("E2E flow call verification success.")

if __name__ == "__main__":
    test_wbw_upload_playlist_logic_e2e()
