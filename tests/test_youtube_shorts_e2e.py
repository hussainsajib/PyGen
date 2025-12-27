import pytest
from unittest.mock import patch, MagicMock
from processes.processes import create_wbw_video_job

@pytest.fixture
def mock_deps():
    with patch("processes.processes.generate_video") as mock_gen, \
         patch("processes.processes.extract_frame") as mock_frame, \
         patch("processes.processes.record_media_asset") as mock_record, \
         patch("processes.processes.upload_to_youtube") as mock_upload, \
         patch("processes.processes.anyio.from_thread.run") as mock_anyio_run:
        
        mock_gen.return_value = {
            "video": "test_video.mp4",
            "info": "test_info.txt",
            "is_short": True,
            "reciter": "ar.alafasy"
        }
        mock_upload.return_value = "video_id_123"
        
        yield {
            "gen": mock_gen,
            "upload": mock_upload
        }

def test_wbw_shorts_upload_flow(mock_deps):
    # This test verifies that create_wbw_video_job correctly triggers upload_to_youtube
    # with the is_short flag preserved.
    
    create_wbw_video_job(
        surah=1, start_verse=1, end_verse=1, 
        reciter="ar.alafasy", is_short=True,
        upload_after_generation=True
    )
    
    # Verify upload_to_youtube was called with is_short=True in the details
    args, kwargs = mock_deps["upload"].call_args
    details = args[0]
    assert details["is_short"] is True
