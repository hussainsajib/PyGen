import pytest
from db_ops.crud_mushaf import get_mushaf_page_data, get_mushaf_page_data_structured

def test_mushaf_basmallah_suppression_page_1():
    """
    Surah 1 (Page 1) should NOT have a separate basmallah line type
    because Basmallah is Ayah 1.
    """
    page_data = get_mushaf_page_data(1)
    # Check if any line has type 'basmallah' and surah 1
    basmallah_lines = [l for l in page_data if l["line_type"] == "basmallah" and l["surah_number"] == 1]
    assert len(basmallah_lines) == 0

def test_mushaf_basmallah_suppression_surah_9():
    """
    Surah 9 should NOT have a basmallah line type.
    Surah 9 starts on Page 187.
    """
    page_data = get_mushaf_page_data(187)
    # Check if any line has type 'basmallah' and surah 9
    basmallah_lines = [l for l in page_data if l["line_type"] == "basmallah" and l["surah_number"] == 9]
    assert len(basmallah_lines) == 0

def test_mushaf_basmallah_presence_other_surah():
    """
    Surah 2 (Page 2) SHOULD have a basmallah line type.
    """
    page_data = get_mushaf_page_data(2)
    basmallah_lines = [l for l in page_data if l["line_type"] == "basmallah"]
    assert len(basmallah_lines) > 0
