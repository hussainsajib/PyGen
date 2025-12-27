import pytest
from unittest.mock import patch, MagicMock
from processes import video_utils, video_configs

@pytest.mark.asyncio
async def test_generate_video_uses_configured_threads():
    # Mock all external dependencies to isolate generate_video
    with patch("processes.video_utils.read_surah_data"), \
         patch("processes.video_utils.download_mp3_temp"), \
         patch("processes.video_utils.AudioFileClip"), \
         patch("processes.video_utils.read_text_data"), \
         patch("processes.video_utils.read_translation"), \
         patch("processes.video_utils.read_timestamp_data"), \
         patch("anyio.from_thread.run"), \
         patch("processes.video_utils.generate_intro"), \
         patch("processes.video_utils.create_ayah_clip"), \
         patch("processes.video_utils.generate_outro"), \
         patch("processes.video_utils.concatenate_videoclips") as mock_concat, \
         patch("processes.video_utils.generate_details"), \
         patch("processes.video_utils.get_wbw_timestamps"): # Mock WBW specific dep

        # Setup mock reciter return for anyio run
        mock_reciter = MagicMock()
        mock_reciter.wbw_database = None
        mock_reciter.eng_name = "Test_Reciter"
        patch("anyio.from_thread.run", return_value=mock_reciter).start()
        
        # Setup mock final video
        mock_final_video = MagicMock()
        mock_concat.return_value = mock_final_video
        
        # Setup mock timestamp data to ensure loop runs
        # timestamp data format: [surah_num, ayah, gstart_ms, gend_ms, seg_str]
        patch("processes.video_utils.read_timestamp_data", return_value=[[1, 1, 0, 1000, "seg1"]]).start()
        
        # Call the function
        # generate_video(surah_number, start_verse, end_verse, reciter_key, is_short)
        video_utils.generate_video(1, 1, 1, "ar.alafasy", False)
        
        # Verify write_videofile was called with the correct threads argument
        assert mock_final_video.write_videofile.called
        
        # Get the kwargs of the call
        _, kwargs = mock_final_video.write_videofile.call_args
        
        # Assert threads argument matches config
        assert "threads" in kwargs
        assert kwargs["threads"] == video_configs.VIDEO_ENCODING_THREADS
