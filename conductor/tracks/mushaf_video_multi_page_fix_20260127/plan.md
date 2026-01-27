# Implementation Plan: Mushaf Video Multi-Page Recitation Fix

This plan details the architectural changes to the Mushaf video chunking logic to support seamless multi-page transitions.

## Phase 1: Engine Refactoring
- [x] Task: Fix `get_surah_page_range` in `db_ops/crud_mushaf.py`.
    - It should correctly identify all pages containing any Ayah of the Surah, not just the page with the Surah header.
- [x] Task: Modify `processes/mushaf_video.py` to implement page-aware chunking.
    - Group `all_aligned_lines` by `page_number` first.
    - Apply `lines_per_page` chunking within each page group.
    - Ensure `chunk_start_ms` and `chunk_end_ms` for each page-specific chunk are calculated correctly relative to the total audio.
- [x] Task: Update header injection logic.
    - Only perform `surah_name` and `basmallah` injection if `idx == 0` (first chunk of the first page).
- [x] Task: Conductor - User Manual Verification 'Multi-Page Engine' (Protocol in workflow.md)

## Phase 2: Verification
- [x] Task: Run `scripts/verify_mushaf_rendering.py` with Surah 87 (spans pages 591-592).
- [x] Task: Visually confirm the page swap occurs and fonts/text update correctly.
