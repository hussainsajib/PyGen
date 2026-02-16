import pytest
from db_ops.crud_mushaf import get_juz_boundaries

def test_juz_2_boundaries_page_range():
    """
    Test that Juz 2 correctly identifies its page range.
    Juz 2 starts at Baqarah 142 (Page 22) and ends at Baqarah 252 (Page 41).
    """
    boundaries = get_juz_boundaries(2)
    assert boundaries is not None
    
    # These are the expected authentic QPC v2 15-line Mushaf boundaries for Juz 2
    assert boundaries["start_page"] == 22
    assert boundaries["end_page"] == 41

def test_juz_1_boundaries_page_range():
    """
    Juz 1 starts at Fatiha 1 (Page 1) and ends at Baqarah 141 (Page 21).
    """
    boundaries = get_juz_boundaries(1)
    assert boundaries is not None
    assert boundaries["start_page"] == 1
    assert boundaries["end_page"] == 21

def test_juz_30_boundaries_page_range():
    """
    Juz 30 starts at Naba 1 (Page 582) and ends at Nas 6 (Page 604).
    """
    boundaries = get_juz_boundaries(30)
    assert boundaries is not None
    assert boundaries["start_page"] == 582
    assert boundaries["end_page"] == 604
