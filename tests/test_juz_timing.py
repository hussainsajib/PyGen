import pytest
from unittest.mock import patch, MagicMock
import numpy as np

@patch('processes.mushaf_video.AudioFileClip')
@patch('processes.mushaf_video.concatenate_audioclips')
@patch('processes.mushaf_video.download_mp3_temp')
@patch('processes.mushaf_video.read_surah_data')
@patch('processes.mushaf_video.get_wbw_timestamps')
@patch('processes.mushaf_video.calculate_juz_offsets')
@patch('processes.mushaf_video.get_surah_page_range')
@patch('processes.mushaf_video.get_mushaf_page_data')
@pytest.mark.asyncio
async def test_prepare_juz_data_package_duration_clipping(
    mock_get_page_data, mock_get_page_range, mock_calc_offsets, mock_get_wbw, 
    mock_read_surah, mock_download, mock_concat, mock_audio_clip
):
    """
    Test that prepare_juz_data_package correctly clips the duration when page range is provided.
    """
    from processes.mushaf_video import prepare_juz_data_package
    
    # Mock boundaries
    boundaries = {
        "verse_mapping": {
            "108": "1-3",
            "109": "1-6"
        }
    }
    
    # Mock Reciter
    reciter_db_obj = MagicMock()
    reciter_db_obj.database = "some_db"
    reciter_db_obj.wbw_database = "wbw_db"

    # Mock Audio clips
    mock_surah_108 = MagicMock()
    mock_surah_108.duration = 10.0
    mock_surah_109 = MagicMock()
    mock_surah_109.duration = 15.0
    mock_audio_clip.side_effect = [mock_surah_108, mock_surah_109]
    
    mock_full_juz_audio = MagicMock()
    mock_full_juz_audio.duration = 30.0
    mock_concat.return_value = mock_full_juz_audio
    
    # Mock offsets
    mock_calc_offsets.return_value = {108: 0.0, 109: 15.0}
    
    # Mock WBW
    mock_get_wbw.side_effect = [
        {"108:1": [[1, 100, 500], [2, 600, 1000]]}, # Simplified
        {"109:1": [[1, 100, 500], [2, 600, 1000]]}
    ]
    # Actually get_wbw_timestamps returns dict with ayah_num as key
    mock_get_wbw.side_effect = [
        {1: [[1, 100, 500], [2, 600, 1000]]}, # 108:1
        {1: [[1, 100, 500], [2, 600, 1000]]}  # 109:1
    ]
    
    # Mock Page Range
    mock_get_page_range.side_effect = [(600, 600), (601, 601)] # 108 is p600, 109 is p601
    
    # Mock Page Data
    # Page 600 has word from 108:1
    mock_get_page_data.side_effect = [
        [{"line_type": "ayah", "words": [{"surah": 108, "ayah": 1, "word": 1}]}], # p600
        [{"line_type": "ayah", "words": [{"surah": 109, "ayah": 1, "word": 2}]}]  # p601
    ]
    
    # Call with relative pages 1 to 2 (which are 600 and 601)
    res = await prepare_juz_data_package(
        juz_number=30, 
        reciter_db_obj=reciter_db_obj, 
        boundaries=boundaries, 
        start_page_relative=1, 
        end_page_relative=2
    )
    
    assert res is not None
    clipped_audio, final_wbw, sorted_pages, offsets, temp_files, surah_clips, bsml_audio = res
    
    # Verify clipping
    # global_start_ms should be 100 (from 108:1 word 1, offset 0)
    # global_end_ms should be 15000 + 1000 = 16000 (from 109:1 word 2, offset 15.0s)
    
    mock_full_juz_audio.subclip.assert_called_with(0.1, 16.0)
    
    # Verify adjusted timestamps
    # 108:1 word 1 was 100, now should be 100 - 100 = 0
    assert final_wbw["108:1"][0][1] == 0
    # 109:1 word 2 was 16000, now should be 16000 - 100 = 15900
    assert final_wbw["109:1"][1][2] == 15900
