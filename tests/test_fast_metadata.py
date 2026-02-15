import pytest
import os
from unittest.mock import patch, MagicMock
from processes.mushaf_fast_video import generate_mushaf_fast

@pytest.mark.asyncio
@patch('processes.mushaf_fast_video.fetch_localized_metadata')
@patch('processes.mushaf_fast_video.read_surah_data')
@patch('processes.mushaf_fast_video.download_mp3_temp')
@patch('processes.mushaf_fast_video.AudioFileClip')
@patch('db_ops.crud_wbw.get_wbw_timestamps')
@patch('processes.mushaf_fast_video.get_surah_page_range')
@patch('processes.mushaf_fast_video.get_mushaf_page_data')
@patch('processes.mushaf_fast_video.align_mushaf_lines_with_timestamps')
@patch('processes.mushaf_fast_video.FFmpegEngine')
@patch('processes.mushaf_fast_video.generate_details')
async def test_generate_mushaf_fast_metadata_creation(
    mock_gen_details, mock_engine, mock_align, mock_page_data, mock_range, 
    mock_wbw, mock_audio_clip, mock_download, mock_read_surah, mock_fetch_meta
):
    """
    Verify that generate_mushaf_fast calls generate_details to create metadata file.
    """
    # Setup mocks
    mock_fetch_meta.return_value = (MagicMock(), MagicMock(), MagicMock())
    mock_read_surah.return_value = "http://example.com/audio.mp3"
    mock_download.return_value = "tmp.mp3"
    mock_audio_clip.return_value = MagicMock(duration=10.0)
    mock_range.return_value = (600, 600)
    mock_page_data.return_value = []
    mock_align.return_value = []
    mock_gen_details.return_value = "exported_data/details/test.txt"
    
    # Mock engine generate
    mock_engine_inst = mock_engine.return_value
    mock_engine_inst.generate = pytest.importorskip("unittest.mock").AsyncMock()
    
    # Mock audio clip write_audiofile
    mock_audio_clip.return_value.write_audiofile = MagicMock()
    
    # Call generate_mushaf_fast
    res = await generate_mushaf_fast(surah_number=108, reciter_key="ar.alafasy", engine_type="ffmpeg")
    
    assert res is not None
    assert "info" in res
    assert res["info"] == "exported_data/details/test.txt"
    
    # Verify generate_details was called
    mock_gen_details.assert_called_once()
