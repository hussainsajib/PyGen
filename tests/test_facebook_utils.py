import pytest
from unittest.mock import MagicMock, patch
from processes.facebook_utils import FacebookClient

@pytest.fixture
def fb_client():
    return FacebookClient(page_access_token="test_token", page_id="test_page_id")

def test_facebook_client_initialization(fb_client):
    assert fb_client.page_access_token == "test_token"
    assert fb_client.page_id == "test_page_id"
    assert fb_client.base_url == "https://graph.facebook.com/v19.0"

@patch("httpx.post")
@patch("builtins.open", new_callable=MagicMock)
def test_upload_standard_video_success(mock_open, mock_post, fb_client):
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {"id": "video_id"})
    mock_open.return_value.__enter__.return_value = MagicMock()
    
    result = fb_client.upload_standard_video(
        video_path="test_video.mp4",
        title="Test Title",
        description="Test Description"
    )
    
    assert result == "video_id"
    mock_post.assert_called_once()
    # Check if correct endpoint was called
    args, kwargs = mock_post.call_args
    assert f"{fb_client.page_id}/videos" in args[0]

@patch("httpx.post")
@patch("builtins.open", new_callable=MagicMock)
def test_upload_reel_success(mock_open, mock_post, fb_client):
    # Simplified Reels upload flow for test
    # 1. Initialize, 2. Upload, 3. Process
    mock_post.side_effect = [
        MagicMock(status_code=200, json=lambda: {"video_id": "vid_id", "upload_url": "url"}), # Init
        MagicMock(status_code=200), # Upload
        MagicMock(status_code=200, json=lambda: {"success": True}) # Publish
    ]
    mock_open.return_value.__enter__.return_value = MagicMock()
    mock_open.return_value.__enter__.return_value.read.return_value = b"test_content"
    
    result = fb_client.upload_reel(
        video_path="test_video.mp4",
        description="Test Reel Description"
    )
    
    assert result == "vid_id"
    assert mock_post.call_count == 3

def test_upload_to_facebook_logic(fb_client):
    with patch.object(fb_client, 'upload_reel', return_value="reel_id") as mock_reel:
        with patch.object(fb_client, 'upload_standard_video', return_value="video_id") as mock_standard:
            # Case 1: Shorts in path
            fb_client.upload_to_facebook("exported_data/shorts/video.mp4", "Title", "Desc")
            mock_reel.assert_called_once()
            mock_standard.assert_not_called()
            
            mock_reel.reset_mock()
            mock_standard.reset_mock()
            
            # Case 2: #Shorts in description
            fb_client.upload_to_facebook("video.mp4", "Title", "Desc #Shorts")
            mock_reel.assert_called_once()
            mock_standard.assert_not_called()
            
            mock_reel.reset_mock()
            mock_standard.reset_mock()
            
            # Case 3: Standard video
            fb_client.upload_to_facebook("video.mp4", "Title", "Desc")
            mock_reel.assert_not_called()
            mock_standard.assert_called_once()
