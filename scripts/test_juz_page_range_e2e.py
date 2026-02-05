import asyncio
import os
from unittest.mock import MagicMock, patch, AsyncMock
from db.models import Job, JobStatus
from processes.background_worker import job_worker
from contextlib import ExitStack

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
    def subclip(self, start, end): return self
    def set_audio(self, audio): return self
    def close(self): pass
    def write_videofile(self, *args, **kwargs): pass
    def resize(self, *args, **kwargs): return self
    def set_duration(self, d):
        self.duration = float(d)
        return self
    def set_position(self, *args, **kwargs): return self
    def set_opacity(self, *args, **kwargs): return self
    def add_mask(self, *args, **kwargs): return self
    def set_end(self, t):
        self.end = t
        return self
    def set_start(self, t, *args, **kwargs):
        self.start = t
        return self

async def run_e2e_test():
    """Simulates enqueuing and processing a partial Juz job."""
    print("--- Starting Juz Page Range E2E Test ---")
    
    # 1. Setup Mocks
    mock_boundaries = {
        "start_surah": 1, "start_ayah": 1, "end_surah": 1, "end_ayah": 7,
        "verse_mapping": {"1": "1-7"}
    }
    mock_wbw = {"1:1": [[1, 0, 1000]], "1:2": [[1, 1000, 2000]], "1:3": [[1, 2000, 3000]]}
    
    def mock_get_page_data(p):
        return [{"line_type": "ayah", "surah_number": 1, "words": [{"surah": 1, "ayah": p, "word": 1, "text": "word"}]}]
    
    def mock_align(lines, timestamps):
        for line in lines: line["start_ms"] = 0; line["end_ms"] = 1000
        return lines

    with ExitStack() as stack:
        # Register all patches
        stack.enter_context(patch("processes.mushaf_video.get_juz_boundaries", return_value=mock_boundaries))
        mock_meta = stack.enter_context(patch("processes.mushaf_video.fetch_localized_metadata", new_callable=AsyncMock))
        stack.enter_context(patch("processes.mushaf_video.AudioFileClip", return_value=MockClip(10.0)))
        stack.enter_context(patch("processes.mushaf_video.read_surah_data", return_value="http://fake.com/audio.mp3"))
        stack.enter_context(patch("processes.mushaf_video.download_mp3_temp", return_value="temp.mp3"))
        stack.enter_context(patch("processes.mushaf_video.calculate_juz_offsets", return_value={1: 0.0}))
        stack.enter_context(patch("processes.mushaf_video.concatenate_audioclips", return_value=MockClip(100.0)))
        stack.enter_context(patch("processes.mushaf_video.get_surah_page_range", return_value=(1, 5)))
        stack.enter_context(patch("processes.mushaf_video.get_mushaf_page_data", side_effect=mock_get_page_data))
        mock_gen_page = stack.enter_context(patch("processes.mushaf_video.generate_mushaf_page_clip", return_value=MockClip(5.0)))
        stack.enter_context(patch("processes.mushaf_video.concatenate_videoclips", return_value=MockClip(100.0)))
        stack.enter_context(patch("processes.mushaf_video.get_wbw_timestamps", return_value=mock_wbw))
        stack.enter_context(patch("processes.mushaf_video.cleanup_temp_file"))
        stack.enter_context(patch("processes.mushaf_video.generate_juz_details", return_value="details.txt"))
        stack.enter_context(patch("processes.mushaf_video.Surah"))
        stack.enter_context(patch("processes.mushaf_video.Reciter"))
        stack.enter_context(patch("processes.mushaf_video.generate_reciter_name_clip", return_value=MockClip(1.0)))
        stack.enter_context(patch("processes.mushaf_video.generate_surah_info_clip", return_value=MockClip(1.0)))
        stack.enter_context(patch("processes.mushaf_video.generate_brand_clip", return_value=MockClip(1.0)))
        stack.enter_context(patch("processes.mushaf_video.ColorClip", return_value=MockClip(1.0)))
        stack.enter_context(patch("processes.mushaf_video.align_mushaf_lines_with_juz_timestamps", side_effect=mock_align))
        stack.enter_context(patch("processes.processes.extract_frame", return_value="shot.png"))
        stack.enter_context(patch("processes.processes.record_media_asset", new_callable=AsyncMock))
        stack.enter_context(patch("processes.processes.get_video_duration", return_value=10.0))
        mock_session_factory = stack.enter_context(patch("processes.background_worker.async_session"))
        
        mock_meta.return_value = (MagicMock(english_name="Mishary", database="db", wbw_database="wbw"), MagicMock(name="english", brand_name="Taqwa"), MagicMock())

        # 2. Prepare mock job
        job = MagicMock(spec=Job)
        job.id = 1
        job.surah_number = 1
        job.surah_name = "Juz 1"
        job.reciter = "ar.alafasy"
        job.job_type = "juz_video"
        job.status = JobStatus.pending
        job.start_page = 2
        job.end_page = 3
        job.is_short = 0
        job.upload_after_generation = 0
        job.playlist_id = None
        job.custom_title = None
        job.background_path = None
        job.lines_per_page = 15
        job.retry_count = 0
        job.max_retries = 3
        
        # Configure mock session
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()
        
        # Mock the result object and its scalar_one_or_none method
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(side_effect=[job, None])
        mock_session.execute.return_value = mock_result
        
        mock_session.commit = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        
        # 3. Process Job
        # We only want to interrupt the SLEEP at the END of the loop, not checkpoints
        async def mock_sleep(t):
            if t == 5: # The loop sleep
                raise InterruptedError("Test Complete")
            await asyncio.sleep(0)

        with patch("asyncio.sleep", side_effect=mock_sleep):
            try:
                await job_worker()
            except InterruptedError:
                pass
        
        # 4. Assertions
        print(f"Generate page call count: {mock_gen_page.call_count}")
        assert mock_gen_page.call_count == 2
        call_args = mock_gen_page.call_args_list
        assert call_args[0][0][1] == 2
        assert call_args[1][0][1] == 3
        print("SUCCESS: Juz Page Range E2E flow verified.")

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
