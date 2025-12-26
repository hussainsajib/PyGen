import pytest
from processes.wbw_utils import segment_words_into_lines

def test_segment_words_with_timestamps():
    words = ["word1", "word2", "word3"]
    translations = ["t1", "t2", "t3"]
    # [word_num, start_ms, end_ms]
    timestamps = [[1, 0, 1000], [2, 1000, 2500], [3, 2500, 4000]]
    
    # Let's say limit is 10, so word1 and word2 fit.
    # word1 (5) + word2 (5) = 10. >= 10. STOP.
    # Segment 1: word1, word2. Duration: 0 to 2500.
    # Segment 2: word3. Duration: 2500 to 4000.
    
    # Implementation not yet supporting timestamps
    from processes.wbw_utils import segment_words_with_timestamps
    segments = segment_words_with_timestamps(words, translations, timestamps, char_limit=10)
    
    assert len(segments) == 2
    assert segments[0]["start_ms"] == 0
    assert segments[0]["end_ms"] == 2500
    assert segments[1]["start_ms"] == 2500
    assert segments[1]["end_ms"] == 4000
