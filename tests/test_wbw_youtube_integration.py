import pytest
from unittest.mock import patch, MagicMock
from processes.processes import create_wbw_video_job

def test_create_wbw_video_job_with_upload():
    with patch("processes.processes.generate_video") as mock_gen, \
         patch("processes.processes.extract_frame") as mock_frame, \
         patch("processes.processes.record_media_asset") as mock_record, \
         patch("processes.processes.upload_to_youtube") as mock_upload, \
         patch("processes.processes.anyio.from_thread.run") as mock_anyio_run:
            
        mock_gen.return_value = {"video": "test.mp4", "reciter": "ar.alafasy"}
        mock_upload.return_value = "video_id_123"
        
        # Test call with upload enabled
        create_wbw_video_job(
            surah=1, 
            start_verse=1, 
            end_verse=1, 
            reciter="ar.alafasy", 
            is_short=True,
            upload_after_generation=True,
            playlist_id="PL123"
        )
        
        # Verify upload was called
        mock_upload.assert_called_once()
        # Verify anyio run was called for recording and status update
        assert mock_anyio_run.call_count >= 2

def test_create_wbw_video_job_without_upload():
    with patch("processes.processes.generate_video") as mock_gen, \
         patch("processes.processes.extract_frame") as mock_frame, \
         patch("processes.processes.record_media_asset") as mock_record, \
         patch("processes.processes.upload_to_youtube") as mock_upload, \
         patch("processes.processes.anyio.from_thread.run") as mock_anyio_run:
            
        mock_gen.return_value = {"video": "test.mp4", "reciter": "ar.alafasy"}
        
        # Test call with upload disabled
        create_wbw_advanced_ayah_clip = create_wbw_video_job(
            surah=1, 
            start_verse=1, 
            end_verse=1, 
            reciter="ar.alafasy", 
            is_short=True,
            upload_after_generation=False
        )
        
        # Verify upload was NOT called
        mock_upload.assert_not_called()
