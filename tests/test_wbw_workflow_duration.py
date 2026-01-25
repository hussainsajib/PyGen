import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from processes.processes import create_wbw_video_job

@pytest.mark.asyncio
async def test_create_wbw_video_job_duration_limit_youtube_skipped():
    """Test that YouTube upload is skipped if duration > 60s for a Short."""
    # Mock data
    surah, start, end, reciter = 1, 1, 7, "ar.alafasy"
    is_short = True
    upload_after_generation = True
    
    mock_video_details = {
        "video": "fake_short.mp4",
        "info": "fake_info.txt",
        "is_short": True,
        "reciter": reciter,
        "surah_number": surah,
        "start_ayah": start,
        "end_ayah": end
    }

    # Mocking dependencies
    with patch("processes.processes.generate_video", new_callable=AsyncMock) as mock_gen, \
         patch("processes.processes.get_video_duration") as mock_duration, \
         patch("processes.processes.upload_to_youtube", new_callable=AsyncMock) as mock_yt, \
         patch("processes.processes._upload_to_facebook_if_enabled", new_callable=AsyncMock) as mock_fb, \
         patch("processes.processes.extract_frame", new_callable=AsyncMock) as mock_frame, \
         patch("processes.processes.record_media_asset", new_callable=AsyncMock), \
         patch("processes.processes._get_target_youtube_channel_id", new_callable=AsyncMock):
        
        mock_gen.return_value = mock_video_details
        mock_frame.return_value = "fake_screenshot.png"
        mock_duration.return_value = 65.0  # > 60s
        
        await create_wbw_video_job(surah, start, end, reciter, is_short=is_short, upload_after_generation=upload_after_generation)
        
        # YouTube should be skipped
        mock_yt.assert_not_called()
        # Facebook should still be called
        mock_fb.assert_called_once()

@pytest.mark.asyncio
async def test_create_wbw_video_job_duration_limit_youtube_allowed():
    """Test that YouTube upload proceeds if duration <= 60s for a Short."""
    # Mock data
    surah, start, end, reciter = 1, 1, 7, "ar.alafasy"
    is_short = True
    upload_after_generation = True
    
    mock_video_details = {
        "video": "fake_short.mp4",
        "info": "fake_info.txt",
        "is_short": True,
        "reciter": reciter,
        "surah_number": surah,
        "start_ayah": start,
        "end_ayah": end
    }

    # Mocking dependencies
    with patch("processes.processes.generate_video", new_callable=AsyncMock) as mock_gen, \
         patch("processes.processes.get_video_duration") as mock_duration, \
         patch("processes.processes.upload_to_youtube", new_callable=AsyncMock) as mock_yt, \
         patch("processes.processes._upload_to_facebook_if_enabled", new_callable=AsyncMock) as mock_fb, \
         patch("processes.processes.extract_frame", new_callable=AsyncMock) as mock_frame, \
         patch("processes.processes.record_media_asset", new_callable=AsyncMock), \
         patch("processes.processes._get_target_youtube_channel_id", new_callable=AsyncMock):
        
        mock_gen.return_value = mock_video_details
        mock_frame.return_value = "fake_screenshot.png"
        mock_duration.return_value = 55.0  # <= 60s
        
        await create_wbw_video_job(surah, start, end, reciter, is_short=is_short, upload_after_generation=upload_after_generation)
        
        # YouTube should be called
        mock_yt.assert_called_once()
        # Facebook should be called
        mock_fb.assert_called_once()
