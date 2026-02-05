import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import os

# Mock class for MoviePy clips
class MockClip:
    def __init__(self, duration=10.0, is_mask=False):
        self.duration = float(duration)
        self.end = self.duration
        self.start = 0.0
        self.audio = self
        self.nchannels = 2
        self.w = 1080
        self.h = 1920
        self.fps = 24
        self.pos = (0, 0)
        if not is_mask:
            self.mask = MockClip(duration=duration, is_mask=True)
        else:
            self.mask = None
    def subclip(self, start, end):
        return self
    def set_audio(self, audio):
        return self
    def close(self):
        pass
    def write_videofile(self, *args, **kwargs):
        pass
    def resize(self, *args, **kwargs):
        return self
    def set_duration(self, d):
        self.duration = float(d)
        return self
    def set_position(self, *args, **kwargs):
        return self
    def set_opacity(self, *args, **kwargs):
        return self
    def add_mask(self, *args, **kwargs):
        return self
    def set_end(self, t):
        self.end = t
        return self
    def set_start(self, t, *args, **kwargs):
        self.start = t
        return self

@pytest.mark.asyncio
async def test_generate_juz_video_page_range_filtering():
    """Verify that generate_juz_video filters pages correctly when a range is provided."""
    
    mock_boundaries = {
        "start_surah": 1,
        "start_ayah": 1,
        "end_surah": 1,
        "end_ayah": 7,
        "verse_mapping": {"1": "1-7"}
    }
    
    mock_wbw = {
        "1:1": [[1, 0, 1000]],
        "1:2": [[1, 1000, 2000]],
        "1:3": [[1, 2000, 3000]]
    }
    
    def mock_get_mushaf_page_data(p):
        return [{
            "line_type": "ayah", 
            "surah_number": 1, 
            "words": [{"surah": 1, "ayah": p, "word": 1, "text": "word"}]
        }]

    def mock_align(lines, timestamps):
        # Add timing to the lines to prevent skipping
        for line in lines:
            line["start_ms"] = 0
            line["end_ms"] = 1000
        return lines

    p1 = patch("processes.mushaf_video.get_juz_boundaries", return_value=mock_boundaries)
    p2 = patch("processes.mushaf_video.fetch_localized_metadata", new_callable=AsyncMock, return_value=(MagicMock(english_name="Mishary", bangla_name="মিশারি", database="db", wbw_database="wbw"), MagicMock(name="english", brand_name="Taqwa"), MagicMock()))
    p3 = patch("processes.mushaf_video.AudioFileClip", return_value=MockClip(10.0))
    p4 = patch("processes.mushaf_video.read_surah_data", return_value="http://fake.com/audio.mp3")
    p5 = patch("processes.mushaf_video.download_mp3_temp", return_value="temp.mp3")
    p6 = patch("processes.mushaf_video.calculate_juz_offsets", return_value={1: 0.0})
    p7 = patch("processes.mushaf_video.concatenate_audioclips", return_value=MockClip(100.0))
    p8 = patch("processes.mushaf_video.get_surah_page_range", return_value=(1, 5))
    p9 = patch("processes.mushaf_video.get_mushaf_page_data", side_effect=mock_get_mushaf_page_data)
    p10 = patch("processes.mushaf_video.generate_mushaf_page_clip", return_value=MockClip(5.0))
    p11 = patch("processes.mushaf_video.concatenate_videoclips", return_value=MockClip(100.0))
    p12 = patch("processes.mushaf_video.get_wbw_timestamps", return_value=mock_wbw)
    p13 = patch("processes.mushaf_video.cleanup_temp_file")
    p14 = patch("processes.mushaf_video.generate_juz_details", return_value="details.txt")
    p15 = patch("processes.mushaf_video.Surah")
    p16 = patch("processes.mushaf_video.Reciter")
    p17 = patch("processes.mushaf_video.async_session")
    p18 = patch("processes.mushaf_video.generate_reciter_name_clip", return_value=MockClip(1.0))
    p19 = patch("processes.mushaf_video.generate_surah_info_clip", return_value=MockClip(1.0))
    p20 = patch("processes.mushaf_video.generate_brand_clip", return_value=MockClip(1.0))
    p21 = patch("processes.mushaf_video.ColorClip", return_value=MockClip(1.0))
    p22 = patch("processes.mushaf_video.align_mushaf_lines_with_juz_timestamps", side_effect=mock_align)

    all_patches = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22]
    
    try:
        started_mocks = [p.start() for p in all_patches]
        mock_gen_page = started_mocks[9]
        
        from processes.mushaf_video import generate_juz_video
        
        # Act: Request pages 2 to 3 (relative)
        # Full range is [1, 2, 3, 4, 5]. rel 2-3 is abs pages 2 and 3.
        result = await generate_juz_video(juz_number=1, reciter_key="ar.alafasy", start_page=2, end_page=3)
        
        assert result is not None
        assert mock_gen_page.call_count == 2
        call_args_list = mock_gen_page.call_args_list
        assert call_args_list[0][0][1] == 2
        assert call_args_list[1][0][1] == 3
    finally:
        for p in all_patches: p.stop()