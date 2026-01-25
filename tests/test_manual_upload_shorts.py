import pytest
from unittest.mock import patch, AsyncMock
from processes.processes import manual_upload_to_youtube
import os

@pytest.mark.asyncio
async def test_manual_upload_shorts_path_resolution():
    # Define a mock short filename
    short_filename = "quran_shorts_1_1_7_mishary.mp4"
    reciter_key = "ar.mishary"
    playlist_id = "PL123"
    details_filename = "details.txt"

    # Mock dependencies
    with patch("processes.processes._get_target_youtube_channel_id", new_callable=AsyncMock) as mock_get_channel_id, \
         patch("processes.processes.upload_to_youtube", new_callable=AsyncMock) as mock_upload, \
         patch("processes.processes.update_media_asset_upload", new_callable=AsyncMock) as mock_update_db:
        
        mock_get_channel_id.return_value = "channel_id"
        mock_upload.return_value = "video_id"

        # Execute the function
        await manual_upload_to_youtube(short_filename, reciter_key, playlist_id, details_filename)

        # Assertions
        # Check what arguments were passed to upload_to_youtube
        mock_upload.assert_called_once()
        call_args = mock_upload.call_args
        video_details = call_args.kwargs.get('video_details') or call_args.args[0]
        
        # We expect the directory to be 'exported_data/shorts' because the filename indicates a short
        # Currently it fails because it uses 'exported_data/videos'
        directory = os.path.dirname(video_details['video'])
        # normalize path separators
        directory = directory.replace(os.sep, "/")
        assert directory.endswith("exported_data/shorts"), f"Expected directory to end with 'exported_data/shorts', got {directory}"