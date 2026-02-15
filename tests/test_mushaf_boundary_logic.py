import pytest
from db_ops.crud_mushaf import group_mushaf_lines_into_scenes

def test_group_scenes_surah_53_case():
    """
    Surah 53 starts with 1 line on page 525, then 15 on page 526.
    With threshold=3, the first scene should contain 1 + 15 lines (total 16).
    """
    lines = [
        {"line_number": 15, "line_type": "surah_name", "page": 525},
        # Page 526 starts here
        {"line_number": 1, "line_type": "basmallah", "page": 526},
        {"line_number": 2, "line_type": "ayah", "page": 526},
        {"line_number": 3, "line_type": "ayah", "page": 526},
        {"line_number": 4, "line_type": "ayah", "page": 526}
    ]
    
    scenes = group_mushaf_lines_into_scenes(lines, threshold=3, max_lines=15)
    
    # Deferred Page 525 (1 line) + Page 526 (4 lines) = 5 lines total
    assert len(scenes) == 1
    assert len(scenes[0]) == 5

def test_short_surah_protection():
    """If the total lines is less than threshold, it should still return 1 scene."""
    lines = [
        {"line_number": 15, "line_type": "surah_name", "page": 1},
        {"line_number": 1, "line_type": "basmallah", "page": 2}
    ]
    scenes = group_mushaf_lines_into_scenes(lines, threshold=3)
    assert len(scenes) == 1
    assert len(scenes[0]) == 2

def test_standard_threshold_met():
    """If 3 lines are on the first page, they stay on the first page."""
    lines = [
        {"line_number": 13, "line_type": "ayah", "page": 1},
        {"line_number": 14, "line_type": "ayah", "page": 1},
        {"line_number": 15, "line_type": "ayah", "page": 1},
        {"line_number": 1, "line_type": "ayah", "page": 2}
    ]
    scenes = group_mushaf_lines_into_scenes(lines, threshold=3)
    assert len(scenes) == 2
    assert len(scenes[0]) == 3
    assert len(scenes[1]) == 1

def test_group_scenes_orphaned_header_refinement():
    """If defer_if_no_ayah is True, defer if 0 ayahs on first page regardless of threshold (within limits)."""
    lines = [
        {"line_number": 14, "line_type": "surah_name", "page": 1},
        {"line_number": 15, "line_type": "basmallah", "page": 1},
        {"line_number": 1, "line_type": "ayah", "page": 2}
    ]
    # Even if threshold was 2, we should still defer if defer_if_no_ayah=True
    scenes = group_mushaf_lines_into_scenes(lines, threshold=2, defer_if_no_ayah=True)
    assert len(scenes) == 1
    assert len(scenes[0]) == 3

def test_group_scenes_header_with_ayah_override():
    """If defer_if_no_ayah is True, and there is 1 ayah, do NOT defer even if below threshold."""
    lines = [
        {"line_number": 14, "line_type": "surah_name", "page": 1},
        {"line_number": 15, "line_type": "ayah", "page": 1},
        {"line_number": 1, "line_type": "ayah", "page": 2}
    ]
    # Total lines on Page 1 = 2. Threshold = 3.
    # Usually it would defer. But since it has an Ayah and defer_if_no_ayah=True, 
    # it MUST NOT defer (render exactly as it appears).
    scenes = group_mushaf_lines_into_scenes(lines, threshold=3, defer_if_no_ayah=True)
    assert len(scenes) == 2
    assert len(scenes[0]) == 2
    assert len(scenes[1]) == 1
