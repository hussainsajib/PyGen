# Implementation Plan: Mushaf Video Header and Basmallah Visibility Fix

This plan details the fixes for Basmallah highlighting and the persistent visibility of headers and Basmallah in Mushaf videos.

## Phase 1: Implementation
- [x] Task: Modify `processes/mushaf_video.py` to adjust timing logic for injected headers and Basmallah.
    - Set `end_ms` for `surah_name` and `basmallah` to the maximum `end_ms` of any line in the current chunk.
- [x] Task: Modify `factories/single_clip.py` to disable highlighting for specific line types.
    - Add a check in `generate_mushaf_page_clip` to skip the `ColorClip` highlighting logic if `l_type` is `basmallah`.
- [x] Task: Conductor - User Manual Verification 'Visibility and Highlighting Fix' (Protocol in workflow.md)

## Phase 2: Verification
- [x] Task: Run `scripts/verify_mushaf_rendering.py` with Surah 108 to visually confirm:
    - No highlighting on Basmallah.
    - Header and Basmallah remain visible until the page turns.
