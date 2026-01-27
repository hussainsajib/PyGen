import pytest
from unittest.mock import MagicMock, patch, AsyncMock, call
from contextlib import ExitStack
from processes.mushaf_video import generate_mushaf_video

@pytest.mark.asyncio
async def test_mushaf_header_injection_when_missing():
    """
    Test that a 'surah_name' line is injected into the first chunk
    if it is missing from the page data.
    """
    with ExitStack() as stack:
        # Mock dependencies
        mock_fetch_meta = stack.enter_context(patch("processes.mushaf_video.fetch_localized_metadata", new_callable=AsyncMock))
        mock_read_audio = stack.enter_context(patch("processes.mushaf_video.read_surah_data"))
        mock_download = stack.enter_context(patch("processes.mushaf_video.download_mp3_temp"))
        mock_page_range = stack.enter_context(patch("processes.mushaf_video.get_surah_page_range"))
        mock_page_data = stack.enter_context(patch("processes.mushaf_video.get_mushaf_page_data"))
        mock_align = stack.enter_context(patch("processes.mushaf_video.align_mushaf_lines_with_timestamps"))
        mock_session_cls = stack.enter_context(patch("processes.mushaf_video.async_session", new_callable=MagicMock))
        
        mock_gen_clip = stack.enter_context(patch("processes.mushaf_video.generate_mushaf_page_clip"))
        mock_gen_bg = stack.enter_context(patch("processes.mushaf_video.generate_background"))
        mock_gen_reciter = stack.enter_context(patch("processes.mushaf_video.generate_reciter_name_clip"))
        mock_gen_surah = stack.enter_context(patch("processes.mushaf_video.generate_surah_info_clip"))
        mock_gen_brand = stack.enter_context(patch("processes.mushaf_video.generate_brand_clip"))
        
        mock_audio_clip = stack.enter_context(patch("processes.mushaf_video.AudioFileClip"))
        mock_text_clip = stack.enter_context(patch("processes.mushaf_video.TextClip"))
        mock_color_clip = stack.enter_context(patch("processes.mushaf_video.ColorClip"))
        mock_composite_clip = stack.enter_context(patch("processes.mushaf_video.CompositeVideoClip"))
        mock_concat = stack.enter_context(patch("processes.mushaf_video.concatenate_videoclips"))
        mock_details = stack.enter_context(patch("processes.mushaf_video.generate_details"))
        
        mock_surah_cls = stack.enter_context(patch("processes.mushaf_video.Surah"))
        mock_reciter_cls = stack.enter_context(patch("processes.mushaf_video.Reciter"))
        mock_config = stack.enter_context(patch("processes.mushaf_video.config_manager"))

        # Setup basic mocks
        mock_reciter_obj = MagicMock()
        mock_reciter_obj.wbw_database = None # Disable WBW for this test to simplify
        mock_reciter_obj.database = "surah_db"
        
        mock_lang = MagicMock()
        mock_lang.name = "english"
        
        mock_surah_obj = MagicMock()
        
        mock_fetch_meta.return_value = (mock_reciter_obj, mock_lang, mock_surah_obj)
        mock_read_audio.return_value = "http://url"
        mock_download.return_value = "/tmp/f"
        mock_audio_clip.return_value.duration = 10.0
        
        # Single page, start to end
        mock_page_range.return_value = (10, 10)
        
        # Data WITHOUT header
        mock_page_data.return_value = [{"surah_number": 5, "words": [], "page_number": 10}] 
        # align returns the list used for chunking
        mock_align.return_value = [
            {
                "page_number": 10,
                "line_number": 1,
                "line_type": "ayah",
                "surah_number": 5,
                "words": [],
                "start_ms": 0,
                "end_ms": 5000
            }
        ]
        
        mock_concat.return_value = MagicMock()
        mock_surah_cls.return_value.total_ayah = 10
        
        # Run
        await generate_mushaf_video(5, "reciter", lines_per_page=15)
        
        # Verify generate_mushaf_page_clip was called
        assert mock_gen_clip.called
        
        # Get arguments passed to generate_mushaf_page_clip
        # It's called for each chunk. We have 1 chunk.
        args, _ = mock_gen_clip.call_args
        chunk_passed = args[0]
        
        # Verify header was injected at index 0
        # Now it should be Header at index 0 and Bismillah at index 1
        assert chunk_passed[0]["line_type"] == "surah_name"
        assert chunk_passed[1]["line_type"] == "basmallah"
        assert chunk_passed[2]["line_type"] == "ayah"

@pytest.mark.asyncio
async def test_mushaf_header_preservation_when_present():
    """
    Test that a 'surah_name' line is NOT duplicated if already present.
    """
    with ExitStack() as stack:
        # Mock dependencies (same as above)
        mock_fetch_meta = stack.enter_context(patch("processes.mushaf_video.fetch_localized_metadata", new_callable=AsyncMock))
        mock_read_audio = stack.enter_context(patch("processes.mushaf_video.read_surah_data"))
        mock_download = stack.enter_context(patch("processes.mushaf_video.download_mp3_temp"))
        mock_page_range = stack.enter_context(patch("processes.mushaf_video.get_surah_page_range"))
        mock_page_data = stack.enter_context(patch("processes.mushaf_video.get_mushaf_page_data"))
        mock_align = stack.enter_context(patch("processes.mushaf_video.align_mushaf_lines_with_timestamps"))
        mock_session_cls = stack.enter_context(patch("processes.mushaf_video.async_session", new_callable=MagicMock))
        
        mock_gen_clip = stack.enter_context(patch("processes.mushaf_video.generate_mushaf_page_clip"))
        mock_gen_bg = stack.enter_context(patch("processes.mushaf_video.generate_background"))
        mock_gen_reciter = stack.enter_context(patch("processes.mushaf_video.generate_reciter_name_clip"))
        mock_gen_surah = stack.enter_context(patch("processes.mushaf_video.generate_surah_info_clip"))
        mock_gen_brand = stack.enter_context(patch("processes.mushaf_video.generate_brand_clip"))
        
        mock_audio_clip = stack.enter_context(patch("processes.mushaf_video.AudioFileClip"))
        mock_text_clip = stack.enter_context(patch("processes.mushaf_video.TextClip"))
        mock_color_clip = stack.enter_context(patch("processes.mushaf_video.ColorClip"))
        mock_composite_clip = stack.enter_context(patch("processes.mushaf_video.CompositeVideoClip"))
        mock_concat = stack.enter_context(patch("processes.mushaf_video.concatenate_videoclips"))
        mock_details = stack.enter_context(patch("processes.mushaf_video.generate_details"))
        
        mock_surah_cls = stack.enter_context(patch("processes.mushaf_video.Surah"))
        mock_reciter_cls = stack.enter_context(patch("processes.mushaf_video.Reciter"))
        mock_config = stack.enter_context(patch("processes.mushaf_video.config_manager"))

        # Setup mocks
        mock_reciter_obj = MagicMock()
        mock_reciter_obj.wbw_database = None
        mock_reciter_obj.database = "surah_db"
        
        mock_lang = MagicMock()
        mock_lang.name = "english"
        
        mock_surah_obj = MagicMock()
        
        mock_fetch_meta.return_value = (mock_reciter_obj, mock_lang, mock_surah_obj)
        mock_read_audio.return_value = "http://url"
        mock_download.return_value = "/tmp/f"
        mock_audio_clip.return_value.duration = 10.0
        mock_page_range.return_value = (10, 10)
        
        # Data WITH header
        mock_page_data.return_value = [{"surah_number": 5, "words": [], "page_number": 10}]
        mock_align.return_value = [
            {
                "page_number": 10,
                "line_number": 1,
                "line_type": "surah_name", # Existing header
                "surah_number": 5,
                "words": [],
                "start_ms": 0,
                "end_ms": 5000
            },
            {
                "page_number": 10,
                "line_number": 2,
                "line_type": "basmallah", # Existing Bismillah
                "surah_number": 5,
                "words": [],
                "start_ms": 0,
                "end_ms": 5000
            },
            {
                "page_number": 10,
                "line_number": 3,
                "line_type": "ayah",
                "surah_number": 5,
                "words": [],
                "start_ms": 0,
                "end_ms": 5000
            }
        ]
        
        mock_concat.return_value = MagicMock()
        mock_surah_cls.return_value.total_ayah = 10
        
        await generate_mushaf_video(5, "reciter", lines_per_page=15)
        
        args, _ = mock_gen_clip.call_args
        chunk_passed = args[0]
        
        # Verify NO duplicate
        assert len(chunk_passed) == 3 
        assert chunk_passed[0]["line_type"] == "surah_name"
        assert chunk_passed[1]["line_type"] == "basmallah"
        assert chunk_passed[2]["line_type"] == "ayah"