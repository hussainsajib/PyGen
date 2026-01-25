import asyncio
import os
from processes.processes import manual_upload_to_youtube
from unittest.mock import patch, AsyncMock

async def verify_paths():
    print("Verifying path resolution for manual upload...")
    
    test_cases = [
        {
            "filename": "quran_shorts_2_127_129_maher_al_muaiqly.mp4",
            "expected_dir": "exported_data/shorts",
            "is_short": True
        },
        {
            "filename": "quran_video_1_mishary.mp4",
            "expected_dir": "exported_data/videos",
            "is_short": False
        }
    ]
    
    for case in test_cases:
        print(f"\nTesting filename: {case['filename']}")
        
        with patch("processes.processes._get_target_youtube_channel_id", new_callable=AsyncMock) as mock_channel, \
             patch("processes.processes.upload_to_youtube", new_callable=AsyncMock) as mock_upload, \
             patch("processes.processes.update_media_asset_upload", new_callable=AsyncMock):
            
            mock_channel.return_value = "test_channel"
            mock_upload.return_value = "test_video_id"
            
            await manual_upload_to_youtube(
                video_filename=case['filename'],
                reciter_key="test_reciter",
                playlist_id="test_playlist",
                details_filename="test_details.txt"
            )
            
            call_args = mock_upload.call_args
            video_details = call_args.kwargs.get('video_details') or call_args.args[0]
            
            actual_path = video_details['video']
            actual_dir = os.path.dirname(actual_path).replace(os.sep, "/")
            actual_is_short = video_details['is_short']
            
            print(f"  Resolved path: {actual_path}")
            print(f"  Is short flag: {actual_is_short}")
            
            assert actual_dir.endswith(case['expected_dir']), f"Failed directory match for {case['filename']}. Expected {case['expected_dir']}, got {actual_dir}"
            assert actual_is_short == case['is_short'], f"Failed is_short match for {case['filename']}. Expected {case['is_short']}, got {actual_is_short}"
            
            print(f"  SUCCESS: Path and flags for {case['filename']} are correct.")

if __name__ == "__main__":
    asyncio.run(verify_paths())
