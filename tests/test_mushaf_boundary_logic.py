import pytest
from db_ops.crud_mushaf import group_mushaf_lines_into_scenes

def test_defer_only_if_zero_ayah_case_1_defer():
    """
    Case 1: Surah starting with ONLY Header/Basmallah on first page (must defer).
    Page 1: Header, Basmalah
    Page 2: Ayah 1, Ayah 2
    Expected:
    Scene 1: Header, Basmalah, Ayah 1, Ayah 2 (all from Page 1 and 2 combined)
    """
    lines = [
        # Page 1 content (Orphaned)
        {'line_type': 'surah_name', 'page_number': 525, 'sura_number': 53},
        {'line_type': 'basmallah', 'page_number': 525, 'sura_number': 53},
        # Page 2 content
        {'line_type': 'ayah', 'page_number': 526, 'sura_number': 53, 'ayah_number': 1},
        {'line_type': 'ayah', 'page_number': 526, 'sura_number': 53, 'ayah_number': 2},
    ]

    # We expect 'defer_if_no_ayah=True' to trigger the merge
    scenes = group_mushaf_lines_into_scenes(lines, defer_if_no_ayah=True)

    # Should be 1 scene total, merging page 525 and 526
    assert len(scenes) == 1
    assert len(scenes[0]) == 4
    assert scenes[0][0]['line_type'] == 'surah_name'
    assert scenes[0][2]['line_type'] == 'ayah'


def test_defer_only_if_zero_ayah_case_2_no_defer():
    """
    Case 2: Surah starting with Header + at least 1 Ayah on first page (must NOT defer).
    Page 1: Header, Basmalah, Ayah 1
    Page 2: Ayah 2
    Expected:
    Scene 1: Header, Basmalah, Ayah 1
    Scene 2: Ayah 2
    """
    lines = [
        # Page 1 content (Normal)
        {'line_type': 'surah_name', 'page_number': 100, 'sura_number': 2},
        {'line_type': 'basmallah', 'page_number': 100, 'sura_number': 2},
        {'line_type': 'ayah', 'page_number': 100, 'sura_number': 2, 'ayah_number': 1},
        # Page 2 content
        {'line_type': 'ayah', 'page_number': 101, 'sura_number': 2, 'ayah_number': 2},
    ]

    scenes = group_mushaf_lines_into_scenes(lines, defer_if_no_ayah=True)

    # Should remain 2 scenes
    assert len(scenes) == 2
    # Scene 1 has 3 items
    assert len(scenes[0]) == 3
    # Scene 2 has 1 item
    assert len(scenes[1]) == 1
