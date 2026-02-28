import pytest
import os
import json
import asyncio
from unittest.mock import patch, MagicMock
from processes.processes import create_wbw_fast_job
from db.database import async_session

@pytest.mark.asyncio
async def test_create_wbw_fast_job_ffmpeg_pipeline():
    # We want to test that create_wbw_fast_job internally initializes the ffmpeg engine
    # and processes intro, outro, background, and highlights properly.
    
    with patch("processes.processes.generate_wbw_fast") as mock_generate:
        mock_generate.return_value = {
            "video": "exported_data/videos/fast_ffmpeg_wbw_test.mp4",
            "info": "exported_data/details/test_info.txt",
            "performance": {"engine": "ffmpeg"}
        }
        
        # We need a stub for record_media_asset and others to avoid db writes
        with patch("processes.processes.record_media_asset"), \
             patch("processes.processes.extract_frame"), \
             patch("processes.processes.get_video_duration") as mock_dur:
            
            mock_dur.return_value = 30.0 # Under 60s
            
            res = await create_wbw_fast_job(
                surah=1,
                start_verse=1,
                end_verse=7,
                reciter="ar.alafasy",
                is_short=True,
                upload_after_generation=False,
                background_path="test_bg.jpg"
            )
            
            assert res is not None
            mock_generate.assert_called_once()
            
            # Check if generate_wbw_fast is called with the correct parameters
            kwargs = mock_generate.call_args.kwargs
            assert mock_generate.call_args.args[0] == 1 # surah
            assert mock_generate.call_args.args[1] == 1 # start_verse
            assert mock_generate.call_args.args[2] == 7 # end_verse
            assert mock_generate.call_args.args[3] == "ar.alafasy" # reciter
            assert kwargs.get("engine_type") == "ffmpeg"
            assert kwargs.get("is_short") == True
            assert kwargs.get("background_path") == "test_bg.jpg"
