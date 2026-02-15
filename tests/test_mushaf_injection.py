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
@patch('processes.mushaf_video.get_mushaf_page_data')
@patch('processes.mushaf_video.get_surah_page_range')
@patch('processes.mushaf_video.config_manager')
@patch('processes.mushaf_video.generate_mushaf_page_clip')
@patch('processes.mushaf_video.CompositeVideoClip')
@pytest.mark.asyncio
async def test_generate_mushaf_video_injection(
    mock_composite, mock_page_clip, mock_config, mock_page_range, mock_page_data, 
    mock_fetch_meta, mock_read_surah, mock_download, 
    mock_concat_audio, mock_concat_video, mock_silence, mock_bsml_clip, mock_audio_clip
):
    """
    Integration test for generate_mushaf_video with Basmallah injection.
    """
    from processes.mushaf_video import generate_mushaf_video
    
    # Setup mocks
    mock_config.get.side_effect = lambda key, default=None: "1.5" if key == "MUSHAF_BASMALLAH_SILENCE_DURATION" else default
    mock_page_range.return_value = (1, 1)
    mock_read_surah.return_value = "http://example.com/audio.mp3"
    mock_download.return_value = "tmp.mp3"
    
    # Mock Metadata
    reciter_db_obj = MagicMock()
    reciter_db_obj.database = "some_db"
    reciter_db_obj.wbw_database = None
    mock_fetch_meta.return_value = (reciter_db_obj, MagicMock(), MagicMock())
    
    # Mock Clips
    full_audio_obj = MockClip(60.0)
    mock_audio_clip.return_value = full_audio_obj
    
    bsml_audio_obj = MockClip(3.0)
    mock_bsml_clip.return_value = bsml_audio_obj
    
    silence_obj = MockClip(1.5)
    mock_silence.return_value = silence_obj
    
    mock_page_data.return_value = [
        {"line_type": "ayah", "surah_number": 2, "words": []}
    ]
    
    # Call generate_mushaf_video for Surah 2 (should inject)
    await generate_mushaf_video(2, "ar.alafasy")
    
    # Verify injection calls
    mock_bsml_clip.assert_called_once()
    mock_silence.assert_called_with(1.5)
    mock_concat_audio.assert_called()
    
    # Verify concatenate_audioclips arguments
    # It should be [bsml, silence, full_audio]
    args, _ = mock_concat_audio.call_args
    audio_list = args[0]
    assert len(audio_list) == 3
    assert audio_list[0] == bsml_audio_obj
    assert audio_list[1] == silence_obj
    assert audio_list[2] == full_audio_obj

@patch('processes.mushaf_video.AudioFileClip')
@patch('processes.mushaf_video.get_standard_basmallah_clip')
@patch('processes.mushaf_video.make_silence')
@patch('processes.mushaf_video.concatenate_videoclips')
@patch('processes.mushaf_video.concatenate_audioclips')
@patch('processes.mushaf_video.download_mp3_temp')
@patch('processes.mushaf_video.read_surah_data')
@patch('processes.mushaf_video.fetch_localized_metadata')
@patch('processes.mushaf_video.get_mushaf_page_data')
@patch('processes.mushaf_video.get_surah_page_range')
@patch('processes.mushaf_video.config_manager')
@pytest.mark.asyncio
async def test_generate_mushaf_video_no_injection_surah_1_9(
    mock_config, mock_page_range, mock_page_data, 
    mock_fetch_meta, mock_read_surah, mock_download, 
    mock_concat_audio, mock_concat_video, mock_silence, mock_bsml_clip, mock_audio_clip
):
    """
    Verify that Surah 1 and 9 do NOT have injection.
    """
    from processes.mushaf_video import generate_mushaf_video
    
    mock_page_range.return_value = (1, 1)
    mock_read_surah.return_value = "url"
    mock_download.return_value = "tmp.mp3"
    mock_fetch_meta.return_value = (MagicMock(), MagicMock(), MagicMock())
    mock_audio_clip.return_value = MockClip(10.0)
    mock_page_data.return_value = []

    # Surah 1
    await generate_mushaf_video(1, "ar.alafasy")
    mock_bsml_clip.assert_not_called()
    mock_silence.assert_not_called()
    
    # Surah 9
    mock_bsml_clip.reset_mock()
    mock_silence.reset_mock()
    await generate_mushaf_video(9, "ar.alafasy")
    mock_bsml_clip.assert_not_called()
    mock_silence.assert_not_called()
