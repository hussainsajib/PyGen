import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from contextlib import ExitStack
from processes.mushaf_video import generate_mushaf_video

@pytest.mark.asyncio
async def test_generate_mushaf_video_success():
    """Test the orchestration of Mushaf video generation."""
    
    with ExitStack() as stack:
        # Mock dependencies
        mock_fetch_meta = stack.enter_context(patch("processes.mushaf_video.fetch_localized_metadata", new_callable=AsyncMock))
        mock_read_audio = stack.enter_context(patch("processes.mushaf_video.read_surah_data"))
        mock_download = stack.enter_context(patch("processes.mushaf_video.download_mp3_temp"))
        mock_get_reciter = stack.enter_context(patch("processes.mushaf_video.get_reciter_by_key"))
        mock_get_timestamps = stack.enter_context(patch("processes.mushaf_video.get_wbw_timestamps"))
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
        mock_lang = MagicMock()
        mock_lang.name = "english"
        mock_lang.brand_name = "TestBrand"
        mock_fetch_meta.return_value = (MagicMock(), mock_lang, MagicMock())
        
        mock_read_audio.return_value = "http://example.com/audio.mp3"
        mock_download.return_value = "/tmp/audio.mp3"
        
        mock_audio_instance = MagicMock()
        mock_audio_instance.duration = 10.0
        mock_audio_clip.return_value = mock_audio_instance
        
        mock_page_range.return_value = (1, 1) # Single page
        
        # Mock page data
        mock_page_data.return_value = [{"surah_number": 1, "words": []}]
        mock_align.return_value = [{"start_ms": 0, "end_ms": 5000}]
        
        mock_gen_clip.return_value = MagicMock()
        mock_gen_bg.return_value = MagicMock()
        
        mock_concat_clip = MagicMock()
        mock_concat.return_value = mock_concat_clip
        
        mock_surah_cls.return_value.english_name = "Al-Fatihah"
        mock_surah_cls.return_value.total_ayah = 7
        
        mock_reciter_cls.return_value.english_name = "Mishary"
        
        mock_config.get.return_value = "True"
        
        # Run function
        result = await generate_mushaf_video(1, "ar.alafasy")
        
        # Verify
        assert result is not None
        assert "video" in result
        assert "info" in result
        assert result["surah_number"] == 1
        
        mock_fetch_meta.assert_called_once()
        mock_download.assert_called_once()
        mock_gen_clip.assert_called()
        mock_concat_clip.write_videofile.assert_called_once()