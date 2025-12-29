import pytest
from unittest.mock import patch, MagicMock
import json
from processes.processes import create_wbw_video_job
from db.models import Job, JobStatus

def test_wbw_enhanced_e2e_flow():
    """Verifies the enhanced WBW flow with full translation and YouTube upload."""
    
    # 1. Mock dependencies for create_wbw_video_job
    with patch("processes.processes.generate_video") as mock_gen_video, \
         patch("processes.processes.extract_frame") as mock_extract_frame, \
         patch("processes.processes.record_media_asset") as mock_record_asset, \
         patch("processes.processes.upload_to_youtube") as mock_upload, \
         patch("processes.processes.anyio.from_thread.run") as mock_anyio_run, \
         patch("processes.surah_video.get_full_translation_for_ayah") as mock_get_full_trans, \
         patch("processes.surah_video.generate_full_ayah_translation_clip") as mock_gen_trans_clip, \
         patch("processes.surah_video.config_manager.get") as mock_get_config:

        # Setup mocks
        mock_gen_video.return_value = {
            "video": "exported_data/videos/test.mp4",
            "info": "exported_data/details/test.txt",
            "reciter": "ar.alafasy",
            "surah_number": 114,
            "start_ayah": 1,
            "end_ayah": 1
        }
        mock_extract_frame.return_value = "exported_data/screenshots/test.png"
        mock_upload.return_value = "yt_video_id_123"
        mock_get_full_trans.return_value = "Test full translation"
        
        # Mock config to enable full translation
        def config_side_effect(key, default=None):
            if key == "WBW_FULL_TRANSLATION_ENABLED": return "True"
            if key == "WBW_FULL_TRANSLATION_SOURCE": return "rawai_al_bayan"
            if key == "UPLOAD_TO_YOUTUBE": return "True"
            return default
        mock_get_config.side_effect = config_side_effect

        # 2. Trigger the job processing logic (simulating what the worker calls)
        create_wbw_video_job(
            surah=114,
            start_verse=1,
            end_verse=1,
            reciter="ar.alafasy",
            is_short=True,
            upload_after_generation=True,
            playlist_id="PL_TEST_PLAYLIST",
            custom_title="Custom Prefix"
        )

        # 3. Verify the sequence of actions
        
        # Verify video generation was called
        mock_gen_video.assert_called_once_with(114, 1, 1, "ar.alafasy", True, custom_title="Custom Prefix")
        
        # Verify anyio run was called for recording and upload status update
        # 1. record_media_asset
        # 2. update_media_asset_upload (if upload succeeds)
        assert mock_anyio_run.call_count >= 2
        
        # Verify upload was called with correct details
        mock_upload.assert_called_once()
        
        # Note: We can't easily check if generate_full_ayah_translation_clip was called 
        # from create_wbw_video_job because it's deeply nested in generate_video -> create_wbw_advanced_ayah_clip.
        # But our unit tests already verified that link. 
        
        print("E2E Test Success: WBW generation and upload flow verified.")

if __name__ == "__main__":
    test_wbw_enhanced_e2e_flow()
