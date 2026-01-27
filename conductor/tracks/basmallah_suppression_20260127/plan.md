# Implementation Plan: Basmallah Suppression for Surah 1 and Surah 9

This plan covers the synchronization of web and video components to correctly handle Basmallah visibility for Surahs 1 and 9.

## Phase 1: Backend & Web Fixes
- [x] Task: Modify `db_ops/crud_mushaf.py`.
    - Update `get_mushaf_page_data` to filter out lines where `line_type == 'basmallah'` AND `surah_number` is 1 or 9.
    - Update `get_mushaf_page_data_structured` with the same filtering logic.
- [x] Task: Verify web viewer rendering for Page 1 and Surah 9 start.
- [x] Task: Conductor - User Manual Verification 'Backend & Web Fixes' (Protocol in workflow.md)

## Phase 2: Video Generator Fixes
- [x] Task: Modify `processes/mushaf_video.py`.
    - Update the injection logic to explicitly skip Basmallah injection for `surah_number == 1` (in addition to the existing check for 9).
- [x] Task: Conductor - User Manual Verification 'Video Generator Fixes' (Protocol in workflow.md)

## Phase 3: Verification
- [x] Task: Run `scripts/verify_mushaf_rendering.py` for Page 1 and Surah 9.
- [x] Task: Visually confirm no duplicate/extra Basmallah exists for these Surahs.
