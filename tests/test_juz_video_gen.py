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
    def __gt__(self, other):
        return float(self.duration) > float(other)
    def __lt__(self, other):
        return float(self.duration) < float(other)

@patch('processes.mushaf_video.AudioFileClip')
@patch('processes.mushaf_video.concatenate_videoclips')
@patch('processes.mushaf_video.concatenate_audioclips')
@patch('processes.mushaf_video.download_mp3_temp')
@patch('processes.mushaf_video.read_surah_data')
@patch('processes.mushaf_video.fetch_localized_metadata')
@patch('processes.mushaf_video.get_juz_boundaries')
@patch('processes.mushaf_video.get_mushaf_page_data')
@patch('processes.mushaf_video.generate_mushaf_page_clip')
@patch('processes.mushaf_video.generate_reciter_name_clip')
@patch('processes.mushaf_video.generate_surah_info_clip')
@patch('processes.mushaf_video.generate_brand_clip')
@patch('processes.mushaf_video.get_surah_page_range')
@patch('processes.mushaf_video.get_resolution')
@patch('processes.mushaf_video.prepare_juz_data_package')
@patch('processes.mushaf_video.align_mushaf_lines_with_juz_timestamps')
@patch('processes.mushaf_video.validate_mushaf_assets')
@patch('processes.mushaf_video.ColorClip')
@patch('processes.mushaf_video.CompositeVideoClip')
@pytest.mark.asyncio
async def test_generate_juz_video_integration_clipped(
    mock_composite, mock_color, mock_validate, mock_align, mock_prep, mock_resolution, mock_page_range, mock_brand, mock_surah_info, mock_reciter_info,
    mock_page_clip, mock_page_data, mock_boundaries, mock_fetch_meta, 
    mock_read_surah, mock_download, mock_concat_audio, mock_concat_video, mock_audio_clip
):
    """
    Integration test for generate_juz_video with page clipping.
    """
    from processes.mushaf_video import generate_juz_video
    
    mock_resolution.return_value = (1920, 1080)
    mock_validate.return_value = []
    
    # Mock ColorClip and CompositeVideoClip
    mock_color_inst = MagicMock(spec=MockClip)
    mock_color_inst.set_opacity.return_value = mock_color_inst
    mock_color_inst.set_duration.return_value = mock_color_inst
    mock_color_inst.set_position.return_value = mock_color_inst
    mock_color_inst.resize.return_value = mock_color_inst
    mock_color.return_value = mock_color_inst
    
    mock_composite_inst = MagicMock(spec=MockClip)
    mock_composite_inst.set_duration.return_value = mock_composite_inst
    mock_composite_inst.set_audio.return_value = mock_composite_inst
    mock_composite.return_value = mock_composite_inst

    # Use real-ish object instead of MagicMock for the audio duration logic
    full_audio_obj = MockClip(10.0)
    
    final_wbw = {"108:1": [[1, 0.0, 5000.0], [2, 5000.0, 10000.0]]}
    sorted_pages = [600]
    offsets = {108: 0.0}
    temp_files = ["tmp1.mp3"]
    surah_clips = [MagicMock()]
    bsml_audio = MagicMock()
    
    mock_prep.return_value = (
        full_audio_obj, final_wbw, sorted_pages, offsets, temp_files, surah_clips, bsml_audio
    )
    
    # Mock boundaries
    mock_boundaries.return_value = {
        "verse_mapping": {"108": "1-3"}
    }
    
    # Mock Metadata
    reciter_db_obj = MagicMock()
    reciter_db_obj.database = "some_db"
    mock_fetch_meta.return_value = (reciter_db_obj, MagicMock(), MagicMock())
    
    # Mock Page Data
    mock_page_data.return_value = [
        {"line_type": "ayah", "surah_number": 108, "words": [{"surah": 108, "ayah": 1, "word": 1}]}
    ]
    
    # Mock alignment to return something with timing
    mock_align.return_value = [
        {"line_type": "ayah", "surah_number": 108, "words": [{"surah": 108, "ayah": 1, "word": 1}], "start_ms": 0.0, "end_ms": 5000.0}
    ]
    
    # Mock Concatenate
    mock_final_video = MagicMock(spec=MockClip)
    mock_concat_video.return_value = mock_final_video
    
    # Call generate_juz_video
    res = await generate_juz_video(30, "ar.alafasy", start_page=1, end_page=1)
    
    assert res is not None
    assert "video" in res
    
    # Verify that prepare_juz_data_package was called with correct relative pages
    mock_prep.assert_called_once()
    assert mock_prep.call_args[1]["start_page_relative"] == 1
    assert mock_prep.call_args[1]["end_page_relative"] == 1
    
    # Verify that video was written
    mock_final_video.write_videofile.assert_called_once()