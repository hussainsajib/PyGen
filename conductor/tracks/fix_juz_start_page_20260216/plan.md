# Implementation Plan - Fix Incorrect Start Page for Juz Video Basmallah

## Phase 1: Investigation and Reproduction
- [x] Task: Analyze page number assignment in `processes/mushaf_video.py` and `processes/mushaf_fast_video.py` for Juz videos. [checkpoint: 228bdd6]
    - [x] Review how the first scene's `page_num` is determined during Basmallah injection.
- [x] Task: Create a reproduction script `reproduce_juz_bug.py` to verify the issue.
    - [x] Generate a single frame for the start of Juz 2.
    - [x] Assert that it currently shows the wrong page (e.g., Page 2 instead of Page 22).
- [x] Task: Conductor - User Manual Verification 'Investigation and Reproduction' (Protocol in workflow.md) [checkpoint: 3c1812e]

## Phase 2: Implementation (Database Operations)
- [x] Task: Write failing unit tests in `tests/test_juz_start_page.py`. [checkpoint: 4da10e1]
    - [x] Verify `get_juz_boundaries(2)` returns `start_page=22` and `end_page=41`.
- [x] Task: Implement `get_page_for_verse(surah, ayah, is_last=False)` in `db_ops/crud_mushaf.py`.
- [x] Task: Update `get_juz_boundaries` in `db_ops/crud_mushaf.py` to use `get_page_for_verse`.
- [x] Task: Verify fix with reproduction script.
- [x] Task: Conductor - User Manual Verification 'Implementation (Database Operations)' (Protocol in workflow.md) [checkpoint: 228bdd6]

## Phase 3: Verification (Video Engines)
- [x] Task: Generate a sample frame for Juz 2 using both Standard and Fast engines.
- [x] Task: Verify that the first frame (Basmallah) correctly shows Page 22.
- [x] Task: Conductor - User Manual Verification 'Verification (Video Engines)' (Protocol in workflow.md) [checkpoint: 228bdd6]

## Phase 4: Final Verification and Documentation
- [x] Task: Perform a full visual check by generating a short video snippet for Juz 2.
- [x] Task: Synchronize project documentation.
- [x] Task: Conductor - User Manual Verification 'Final Verification and Documentation' (Protocol in workflow.md) [checkpoint: 228bdd6]
