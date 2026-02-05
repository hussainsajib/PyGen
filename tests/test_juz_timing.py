import pytest
from unittest.mock import MagicMock, patch

# We will implement this function in a new or existing utility file
# For now, let's assume it's in processes/wbw_utils.py or similar
from processes.wbw_utils import calculate_juz_offsets

def test_calculate_juz_offsets_simple():
    """Test timing offsets for a Juz with multiple Surahs."""
    # Mock durations for Surahs in a Juz
    # Juz 1 starts with Surah 1 then Surah 2
    # Surah 1: 10s, Surah 2: 100s
    surah_durations = {
        1: 10.0,
        2: 100.0
    }
    
    # Basmallah duration mock (constant for now)
    bsml_duration = 2.0
    
    surahs_in_juz = [1, 2]
    
    # Logic:
    # Surah 1: Start 0. No Basmallah (Surah 1 exception). End 10.
    # Transition: Surah 2 starts. Needs Basmallah.
    # Basmallah Start: 10. End: 12.
    # Surah 2 Start: 12. End: 112.
    
    offsets = calculate_juz_offsets(surahs_in_juz, surah_durations, bsml_duration)
    
    assert offsets[1] == 0.0
    assert offsets[2] == 12.0

def test_calculate_juz_offsets_with_surah_9():
    """Test timing offsets with Surah 9 (At-Tawbah) exception."""
    # Mock durations
    # Juz 10 ends with Surah 8, Juz 11 starts with Surah 9
    surah_durations = {
        8: 50.0,
        9: 60.0
    }
    bsml_duration = 2.0
    surahs_in_juz = [8, 9]
    
    # Logic:
    # Surah 8: Start 0. End 50.
    # Transition: Surah 9 starts. No Basmallah. 5s gap.
    # Gap Start: 50. End: 55.
    # Surah 9 Start: 55. End: 115.
    
    offsets = calculate_juz_offsets(surahs_in_juz, surah_durations, bsml_duration)
    
    assert offsets[8] == 0.0
    assert offsets[9] == 55.0
