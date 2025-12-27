import pytest
from unittest.mock import patch, MagicMock
from processes.youtube_utils import initialize_upload_request

@pytest.fixture
def mock_video_details():
    return {
        "video": "test_video.mp4",
        "info": "test_info.txt",
        "is_short": True,
        "reciter": "ar.alafasy"
    }

def test_initialize_upload_request_shorts_metadata_short_duration(mock_video_details):
    # Mock get_video_details to return a title and description
    with patch("processes.youtube_utils.get_video_details", return_value=("Test Title", "Test Description")):
        with patch("processes.youtube_utils.get_release_date", return_value=MagicMock()):
            with patch("processes.youtube_utils.VideoFileClip") as mock_clip_class:
                with patch("processes.youtube_utils.MediaFileUpload") as mock_media_upload:
                    # Mock duration to be 60 seconds (Short)
                    mock_clip = mock_clip_class.return_value.__enter__.return_value
                    mock_clip.duration = 60.0
                    
                    mock_youtube = MagicMock()
                    initialize_upload_request(mock_youtube, mock_video_details)
                    
                    # Verify title, description and tags include #Shorts
                    args, kwargs = mock_youtube.videos().insert.call_args
                    body = kwargs["body"]
                    assert "#Shorts" in body["snippet"]["title"]
                    assert "#Shorts" in body["snippet"]["description"]
                    assert "Shorts" in body["snippet"]["tags"]

def test_initialize_upload_request_shorts_metadata_long_duration(mock_video_details):
    # Mock get_video_details to return a title and description
    with patch("processes.youtube_utils.get_video_details", return_value=("Test Title", "Test Description")):
        with patch("processes.youtube_utils.get_release_date", return_value=MagicMock()):
            with patch("processes.youtube_utils.VideoFileClip") as mock_clip_class:
                with patch("processes.youtube_utils.MediaFileUpload") as mock_media_upload:
                    # Mock duration to be 200 seconds (Regular video)
                    mock_clip = mock_clip_class.return_value.__enter__.return_value
                    mock_clip.duration = 200.0
                    
                    mock_youtube = MagicMock()
                    initialize_upload_request(mock_youtube, mock_video_details)
                    
                    # Verify title, description and tags DO NOT include #Shorts
                    args, kwargs = mock_youtube.videos().insert.call_args
                    body = kwargs["body"]
                    assert "#Shorts" not in body["snippet"]["title"]
                    assert "#Shorts" not in body["snippet"]["description"]
                    assert "Shorts" not in body["snippet"]["tags"]