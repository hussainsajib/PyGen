import pytest
from db_ops.crud_mushaf import get_surah_page_range

def test_surah_53_page_range():
    """
    Surah 53 starts on Page 525 (header) and continues to 528.
    The function currently returns (525, 525) which is wrong.
    It should return (525, 528).
    """
    start, end = get_surah_page_range(53)
    assert start == 525
    assert end == 528
