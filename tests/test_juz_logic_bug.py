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
async def test_generate_juz_video_clips_count():
    # Setup mock data for Juz 1 (Surah 1 and Surah 2)
    mock_boundaries = {
        "start_surah": 1,
        "start_ayah": 1,
        "end_surah": 2,
        "end_ayah": 141,
        "verse_mapping": {"1": "1-7", "2": "1-141"}
    }
    
    mock_wbw = {
        "1:1": [[1, 0, 1000], [2, 1000, 2000]],
        "1:2": [[1, 2000, 3000]],
        "2:1": [[1, 0, 1000]]
    }
    
    mock_page_1 = [
        {
            "line_number": 1,
            "line_type": "ayah",
            "surah_number": 1,
            "words": [{"surah": 1, "ayah": 1, "word": 1, "text": "word1"}, {"surah": 1, "ayah": 1, "word": 2, "text": "word2"}]
        },
        {
            "line_number": 2,
            "line_type": "ayah",
            "surah_number": 1,
            "words": [{"surah": 1, "ayah": 2, "word": 1, "text": "word3"}]
        }
    ]
    mock_page_2 = [
        {
            "line_number": 1,
            "line_type": "ayah",
            "surah_number": 2,
            "words": [{"surah": 2, "ayah": 1, "word": 1, "text": "word4"}]
        }
    ]

    p1 = patch("processes.mushaf_video.get_juz_boundaries", return_value=mock_boundaries)
    p2 = patch("processes.mushaf_video.fetch_localized_metadata", new_callable=AsyncMock, return_value=(MagicMock(english_name="Mishary", bangla_name="মিশারি", database="db", wbw_database="wbw"), MagicMock(name="english", brand_name="Taqwa"), MagicMock()))
    p3 = patch("processes.mushaf_video.AudioFileClip", return_value=MockClip(10.0))
    p4 = patch("processes.mushaf_video.read_surah_data", return_value="http://fake.com/audio.mp3")
    p5 = patch("processes.mushaf_video.download_mp3_temp", return_value="temp.mp3")
    p6 = patch("processes.mushaf_video.calculate_juz_offsets", return_value={1: 0.0, 2: 12.0})
    p7 = patch("processes.mushaf_video.concatenate_audioclips", return_value=MockClip(100.0))
    p8 = patch("processes.mushaf_video.get_surah_page_range", side_effect=lambda s: (1, 1) if s == 1 else (2, 2))
    p9 = patch("processes.mushaf_video.get_mushaf_page_data", side_effect=lambda p: mock_page_1 if p == 1 else mock_page_2)
    p10 = patch("processes.mushaf_video.generate_mushaf_page_clip", return_value=MockClip(5.0))
    p11 = patch("processes.mushaf_video.concatenate_videoclips", side_effect=lambda clips, method: MockClip(sum(c.duration for c in clips)))
    p12 = patch("processes.mushaf_video.get_wbw_timestamps")
    p13 = patch("processes.mushaf_video.cleanup_temp_file")
    p14 = patch("processes.mushaf_video.generate_juz_details", return_value="details.txt")
    p15 = patch("processes.mushaf_video.Surah")
    p16 = patch("processes.mushaf_video.Reciter")
    p17 = patch("processes.mushaf_video.async_session")
    p18 = patch("processes.mushaf_video.generate_reciter_name_clip", return_value=MockClip(1.0))
    p19 = patch("processes.mushaf_video.generate_surah_info_clip", return_value=MockClip(1.0))
    p20 = patch("processes.mushaf_video.generate_brand_clip", return_value=MockClip(1.0))
    p21 = patch("processes.mushaf_video.ColorClip", return_value=MockClip(1.0))

    mocks = [p1.start(), p2.start(), p3.start(), p4.start(), p5.start(), p6.start(), p7.start(), p8.start(), p9.start(), p10.start(), p11.start(), p12.start(), p13.start(), p14.start(), p15.start(), p16.start(), p17.start(), p18.start(), p19.start(), p20.start(), p21.start()]
    
    try:
        mock_get_wbw = mocks[11]
        def side_effect_wbw(db, surah, start, end):
            res = {}
            for k, v in mock_wbw.items():
                s, a = map(int, k.split(":"))
                if s == surah:
                    res[a] = v
            return res
        mock_get_wbw.side_effect = side_effect_wbw
        
        mock_concat_video = mocks[10]

        from processes.mushaf_video import generate_juz_video
        result = await generate_juz_video(juz_number=1, reciter_key="ar.alafasy")
        
        assert result is not None
        args, _ = mock_concat_video.call_args
        clips_list = args[0]
        # We expect 2 chunks for page 1 and 1 chunk for page 2 if lines_per_page is small
        # In current logic, it chunks by 15 lines. 
        # Page 1 has 2 lines, Page 2 has 1 line.
        # So we expect 2 page clips (one for each page).
        assert len(clips_list) > 1, f"Expected more than 1 clip, but got {len(clips_list)}"
    finally:
        for p in [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21]:
            p.stop()