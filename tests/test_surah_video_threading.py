import pytest
from unittest.mock import patch, MagicMock
from processes import surah_video, video_configs

@pytest.mark.asyncio
async def test_generate_surah_uses_configured_threads():
    # Mock all external dependencies to isolate generate_surah
    with patch("processes.surah_video.read_surah_data"), \
         patch("processes.surah_video.download_mp3_temp"), \
         patch("processes.surah_video.AudioFileClip"), \
         patch("processes.surah_video.read_text_data"), \
         patch("processes.surah_video.read_translation"), \
         patch("processes.surah_video.read_timestamp_data"), \
         patch("processes.surah_video.anyio.from_thread.run"), \
         patch("processes.surah_video.generate_intro"), \
         patch("processes.surah_video.create_ayah_clip"), \
         patch("processes.surah_video.generate_outro"), \
         patch("processes.surah_video.concatenate_videoclips") as mock_concat, \
         patch("processes.surah_video.generate_details"):

        # Setup mock reciter return for anyio run
        mock_reciter = MagicMock()
        mock_reciter.wbw_database = None
        mock_reciter.eng_name = "Test_Reciter"
        # We need to mock the return value of the async function that fetch_reciter calls
        # But here anyio.from_thread.run is mocked, so we just set its return value
        patch("processes.surah_video.anyio.from_thread.run", return_value=mock_reciter).start()

        # Setup mock final video
        mock_final_video = MagicMock()
        mock_concat.return_value = mock_final_video
        
        # Call the function
        # Note: generate_surah is synchronous in the provided code snippet but might be called in a thread usually.
        # The test itself doesn't strictly need to be async if the function isn't, but pytest-asyncio handles it.
        # Looking at previous code, generate_surah is synchronous.
        surah_video.generate_surah(1, "ar.alafasy")
        
        # Verify write_videofile was called with the correct threads argument
        # We need to check call_args or call_args_list
        # The call signature is write_videofile(output_path, codec=..., ..., threads=X, ...)
        
        assert mock_final_video.write_videofile.called
        
        # Get the kwargs of the call
        _, kwargs = mock_final_video.write_videofile.call_args
        
        # Assert threads argument matches config
        assert "threads" in kwargs
        assert kwargs["threads"] == video_configs.VIDEO_ENCODING_THREADS
