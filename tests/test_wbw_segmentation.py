import pytest
from unittest.mock import patch

# This will fail until implemented
try:
    from processes.wbw_utils import segment_words_into_lines
except ImportError:
    segment_words_into_lines = None

def test_segmentation_module_exists():
    assert segment_words_into_lines is not None

def test_segment_words_into_lines_logic():
    if segment_words_into_lines is None:
        pytest.skip("Function not implemented")
        
    words = ["بِسۡمِ", "ٱللَّهِ", "ٱلرَّحۡمَٰنِ", "ٱلرَّحِيمِ"]
    translations = ["নামে", "আল্লাহ (র)", "পরম করুণাময়", "অসীম দয়ালু"]
    
    # Let's say limit is 15 characters
    # بِسۡمِ (5) + ٱللَّهِ (6) = 11. < 15. Next word.
    # 11 + ٱلرَّحۡمَٰنِ (9) = 20. > 15. STOP.
    # Segment 1: بِسۡمِ ٱللَّهِ ٱلرَّحۡمَٰنِ (3 words)
    # Segment 2: ٱلرَّحِيمِ (1 word)
    
    segments = segment_words_into_lines(words, translations, char_limit=15)
    
    assert len(segments) == 2
    assert segments[0]["words"] == ["بِسۡمِ", "ٱللَّهِ", "ٱلرَّحۡمَٰنِ"]
    assert segments[0]["translations"] == ["নামে", "আল্লাহ (র)", "পরম করুণাময়"]
    assert segments[1]["words"] == ["ٱلرَّحِيمِ"]
    assert segments[1]["translations"] == ["অসীম দয়ালু"]

def test_segment_words_into_lines_soft_limit():
    if segment_words_into_lines is None:
        pytest.skip("Function not implemented")
        
    words = ["word1", "word2long", "word3"]
    translations = ["t1", "t2", "t3"]
    
    # Limit 5
    # word1 (5) = 5. >= 5. STOP.
    # Segment 1: word1
    # Segment 2: word2long
    # Segment 3: word3
    
    segments = segment_words_into_lines(words, translations, char_limit=5)
    assert len(segments) == 3
    assert segments[0]["words"] == ["word1"]
    assert segments[1]["words"] == ["word2long"]
    assert segments[2]["words"] == ["word3"]
