import pytest
from db_ops.crud_mushaf import get_juz_boundaries

def test_get_juz_boundaries_juz_1():
    """Test that Juz 1 boundaries are correctly retrieved."""
    # Juz 1: Surah 1 Ayah 1 to Surah 2 Ayah 141
    boundaries = get_juz_boundaries(1)
    assert boundaries is not None
    assert boundaries["start_surah"] == 1
    assert boundaries["start_ayah"] == 1
    assert boundaries["end_surah"] == 2
    assert boundaries["end_ayah"] == 141
    assert "verse_mapping" in boundaries
    assert boundaries["verse_mapping"]["1"] == "1-7"
    assert boundaries["verse_mapping"]["2"] == "1-141"

def test_get_juz_boundaries_invalid():
    """Test that invalid Juz numbers return None."""
    assert get_juz_boundaries(0) is None
    assert get_juz_boundaries(31) is None
