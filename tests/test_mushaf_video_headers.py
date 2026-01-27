import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from contextlib import ExitStack
from processes.mushaf_video import generate_mushaf_video

@pytest.mark.asyncio
async def test_mushaf_header_and_bsml_injection_timing():
    """
    Test that Surah header and Basmallah are injected into the first chunk
    and their end_ms matches the first Ayah's end_ms (timed visibility).
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
        
        mock_page_range.return_value = (1, 1) 
        
        # Data WITHOUT header/bsml
        # First ayah ends at 2000ms
        mock_page_data.return_value = [{"surah_number": 1, "words": [], "page_number": 1}] 
        mock_align.return_value = [
            {
                "page_number": 1, 
                "line_number": 1, 
                "line_type": "ayah", 
                "surah_number": 1, 
                "words": [], 
                "start_ms": 0, 
                "end_ms": 2000
            }
        ]
        
        mock_concat.return_value = MagicMock()
        mock_surah_cls.return_value.total_ayah = 7
        
        # Run
        await generate_mushaf_video(1, "reciter", lines_per_page=15)
        
        # Verify generate_mushaf_page_clip was called
        assert mock_gen_clip.called
        args, _ = mock_gen_clip.call_args
        chunk_passed = args[0]
        
        # Expect: [Header, BSML, Ayah 1]
        assert chunk_passed[0]["line_type"] == "surah_name"
        assert chunk_passed[1]["line_type"] == "basmallah"
        
        # CHECK TIMING: Should match first ayah's end_ms (2000ms)
        # Current implementation sets it to full chunk duration (10000ms)
        assert chunk_passed[0]["end_ms"] == 2000
        assert chunk_passed[1]["end_ms"] == 2000
