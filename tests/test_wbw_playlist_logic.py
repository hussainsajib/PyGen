import pytest
from unittest.mock import patch, MagicMock
from processes.processes import create_wbw_video_job

@pytest.fixture
def mock_deps():
    test_playlist = {}
    captured_playlist_state = {}

    def capture_playlist_state(*args, **kwargs):
        from processes import youtube_utils
        captured_playlist_state.update(youtube_utils.playlist.copy())
        return "video_id_123"

    with patch("processes.processes.generate_video") as mock_gen, \
         patch("processes.processes.extract_frame") as mock_frame, \
         patch("processes.processes.record_media_asset") as mock_record, \
         patch("processes.processes.upload_to_youtube", side_effect=capture_playlist_state) as mock_upload, \
         patch("processes.processes.anyio.from_thread.run") as mock_anyio_run, \
         patch.dict("processes.youtube_utils.playlist", test_playlist, clear=True):
        
        mock_gen.return_value = {"video": "test.mp4", "reciter": "ar.alafasy"}
        
        yield {
            "gen": mock_gen,
            "upload": mock_upload,
            "playlist_map": test_playlist,
            "captured_state": captured_playlist_state
        }

def test_create_wbw_video_job_playlist_none(mock_deps):
    # Set an existing playlist first
    from processes import youtube_utils
    youtube_utils.playlist["ar.alafasy"] = "EXISTING_PLAYLIST"
    
    create_wbw_video_job(
        surah=1, start_verse=1, end_verse=1, 
        reciter="ar.alafasy", is_short=True,
        upload_after_generation=True,
        playlist_id="none"
    )
    
    # Should be empty in captured state (override removed it)
    assert "ar.alafasy" not in mock_deps["captured_state"]

def test_create_wbw_video_job_playlist_default(mock_deps):
    from processes import youtube_utils
    youtube_utils.playlist["ar.alafasy"] = "DEFAULT_PLAYLIST"
    
    create_wbw_video_job(
        surah=1, start_verse=1, end_verse=1, 
        reciter="ar.alafasy", is_short=True,
        upload_after_generation=True,
        playlist_id="default"
    )
    
    # Should contain the default in captured state (no override applied)
    assert mock_deps["captured_state"]["ar.alafasy"] == "DEFAULT_PLAYLIST"

def test_create_wbw_video_job_playlist_override(mock_deps):
    create_wbw_video_job(
        surah=1, start_verse=1, end_verse=1, 
        reciter="ar.alafasy", is_short=True,
        upload_after_generation=True,
        playlist_id="REAL_PLAYLIST_ID"
    )
    
    assert mock_deps["captured_state"]["ar.alafasy"] == "REAL_PLAYLIST_ID"
