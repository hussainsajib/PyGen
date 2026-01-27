import pytest
from db_ops.crud_mushaf import get_surah_page_range

def test_get_surah_page_range_87():
    """
    Surah 87 should span Pages 591 and 592.
    """
    start_page, end_page = get_surah_page_range(87)
    assert start_page == 591
    assert end_page == 592

def test_get_surah_page_range_1():
    """
    Surah 1 should be only on Page 1.
    """
    start_page, end_page = get_surah_page_range(1)
    assert start_page == 1
    assert end_page == 1

def test_get_surah_page_range_2():
    """
    Surah 2 spans many pages.
    Starts on Page 2, ends on Page 49.
    """
    start_page, end_page = get_surah_page_range(2)
    assert start_page == 2
    assert end_page == 49
