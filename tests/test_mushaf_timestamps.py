import pytest
from db_ops.crud_mushaf import align_mushaf_lines_with_timestamps

def test_align_mushaf_lines_success():
    """Test aligning Mushaf lines with WBW timestamps."""
    # Mock page data (subset of Page 1)
    page_data = [
        {
            "line_number": 2,
            "words": [
                {"id": 1, "ayah": 1, "word": 1, "text": "ﱁ"},
                {"id": 2, "ayah": 1, "word": 2, "text": "ﱂ"},
                {"id": 3, "ayah": 1, "word": 3, "text": "ﱃ"},
                {"id": 4, "ayah": 1, "word": 4, "text": "ﱄ"},
                {"id": 5, "ayah": 1, "word": 5, "text": "ﱅ"}
            ]
        },
        {
            "line_number": 3,
            "words": [
                {"id": 6, "ayah": 2, "word": 1, "text": "ﱆ"},
                {"id": 7, "ayah": 2, "word": 2, "text": "ﱇ"}
            ]
        }
    ]
    
    # Mock WBW timestamps
    # Format: { ayah_num: [[word_num, start_ms, end_ms], ...] }
    wbw_timestamps = {
        1: [
            [1, 0, 500], [2, 500, 1000], [3, 1000, 1500], 
            [4, 1500, 2000], [5, 2000, 2500]
        ],
        2: [
            [1, 2500, 3000], [2, 3000, 3500]
        ]
    }
    
    aligned_lines = align_mushaf_lines_with_timestamps(page_data, wbw_timestamps)
    
    assert aligned_lines[0]["start_ms"] == 0
    assert aligned_lines[0]["end_ms"] == 2500
    assert aligned_lines[1]["start_ms"] == 2500
    assert aligned_lines[1]["end_ms"] == 3500

def test_align_mushaf_lines_missing_words():
    """Test alignment when a line has no words (e.g. surah_name)."""
    page_data = [{"line_number": 1, "words": []}]
    wbw_timestamps = {1: [[1, 0, 500]]}
    
    aligned_lines = align_mushaf_lines_with_timestamps(page_data, wbw_timestamps)
    assert aligned_lines[0]["start_ms"] is None
    assert aligned_lines[0]["end_ms"] is None
