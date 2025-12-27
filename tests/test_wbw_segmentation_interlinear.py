import pytest
from processes.wbw_utils import segment_words_with_timestamps

def test_segmentation_interlinear_behavior():
    words = ["word1", "word2", "word3"]
    translations = ["very_long_translation_1", "short", "short"]
    # timestamps: [word_num, start_ms, end_ms]
    timestamps = [[1, 0, 1000], [2, 1000, 2000], [3, 2000, 3000]]
    
    # In standard mode (heuristic based on Arabic only), they might all fit in one line if char_limit is 20
    # word1 (5) + word2 (5) + word3 (5) + 2 spaces = 17. Fits.
    standard_segments = segment_words_with_timestamps(words, translations, timestamps, char_limit=20)
    assert len(standard_segments) == 1
    
    # In interlinear mode, we want it to account for the long translation.
    # translation1 (23) already exceeds 20. So it should break after first word.
    # We need to update the function to support this.
    interlinear_segments = segment_words_with_timestamps(
        words, translations, timestamps, char_limit=20, 
        interlinear=True, translation_ratio=1.0
    )
    
    # Expected: 2 segments.
    # Seg 1: word1 (max(5, 23) = 23. Exceeds 20. Break.)
    # Seg 2: word2, word3 (max(5, 5) + 1 + max(5, 5) = 11. Fits.)
    assert len(interlinear_segments) == 2
    assert interlinear_segments[0]["words"] == ["word1"]
    assert interlinear_segments[1]["words"] == ["word2", "word3"]
