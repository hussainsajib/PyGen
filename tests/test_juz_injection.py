import pytest
from unittest.mock import patch, MagicMock
import os

class MockClip:
    def __init__(self, d=10.0):
        self.duration = float(d)
    def close(self):
        pass
    def subclip(self, s, e):
        return MockClip(float(e)-float(s))
    def set_audio(self, a):
        return self
    def set_duration(self, d):
        self.duration = float(d)
        return self
    def set_opacity(self, o):
        return self
    def set_position(self, p):
        return self
    def resize(self, *args, **kwargs):
        return self
    def write_videofile(self, *args, **kwargs):
        pass
    def __float__(self):
        return float(self.duration)

@patch('processes.mushaf_video.AudioFileClip')
@patch('processes.mushaf_video.get_standard_basmallah_clip')
@patch('processes.mushaf_video.make_silence')
@patch('processes.mushaf_video.concatenate_videoclips')
@patch('processes.mushaf_video.concatenate_audioclips')
@patch('processes.mushaf_video.download_mp3_temp')
@patch('processes.mushaf_video.read_surah_data')
@patch('processes.mushaf_video.fetch_localized_metadata')
@patch('processes.mushaf_video.get_juz_boundaries')
@patch('processes.mushaf_video.get_mushaf_page_data')
@patch('processes.mushaf_video.get_surah_page_range')
@patch('processes.mushaf_video.config_manager')
@patch('processes.mushaf_video.generate_mushaf_page_clip')
@patch('processes.mushaf_video.CompositeVideoClip')
@patch('processes.mushaf_video.get_resolution')
@patch('processes.mushaf_video.get_wbw_timestamps')
@pytest.mark.asyncio
async def test_prepare_juz_data_package_injection(
    mock_wbw, mock_res, mock_composite, mock_page_clip, mock_config, mock_page_range, mock_page_data, 
    mock_boundaries, mock_fetch_meta, mock_read_surah, mock_download, 
    mock_concat_audio, mock_concat_video, mock_silence, mock_bsml_clip, mock_audio_clip
):
    from processes.mushaf_video import prepare_juz_data_package
    
    # Setup mocks
    mock_config.get.return_value = "1.0"
    mock_boundaries.return_value = {
        "verse_mapping": {"108": "1-3", "109": "1-6"}
    }
    mock_read_surah.return_value = "url"
    mock_download.return_value = "tmp.mp3"
    mock_page_range.return_value = (600, 600)
    mock_wbw.return_value = {1: [[1, 0.0, 5000.0]]}
    mock_page_data.return_value = [
        {"line_type": "ayah", "surah_number": 108, "words": [{"surah": 108, "ayah": 1, "word": 1}]}
    ]
    
    # Mock Metadata
    reciter_db_obj = MagicMock()
    reciter_db_obj.database = "db"
    reciter_db_obj.wbw_database = "db.sqlite"
    
    # Mock Clips
    mock_audio_clip.return_value = MockClip(10.0) # Surah clips
    mock_bsml_clip.return_value = MockClip(3.0)
    mock_silence.return_value = MockClip(1.0)
    mock_concat_audio.side_effect = lambda clips: MockClip(sum(float(c.duration) for c in clips))
    
    # Call prepare_juz_data_package
    res = await prepare_juz_data_package(30, reciter_db_obj, mock_boundaries.return_value)
    
    assert res is not None
    full_audio, timestamps, sorted_pages, offsets, temp_files, surah_clips, bsml_audio = res
    
    # Verify injection for Surah 108 (first) and 109
    # Each should have Basmallah + Silence
    # Total clips in concat: (bsml + sil + s108) + (bsml + sil + s109) = 6
    args, _ = mock_concat_audio.call_args
    audio_list = args[0]
    assert len(audio_list) == 6
    
    # Check offsets
    # s108 offset should be bsml + sil = 4.0
    # s109 offset should be s108_offset + s108_dur + bsml + sil = 4 + 10 + 4 = 18.0
    assert offsets[108] == 4.0
    assert offsets[109] == 18.0
