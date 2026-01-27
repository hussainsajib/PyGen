# Implementation Plan: Mushaf Video Full Text Visibility and Highlighting

This plan covers the transition of Mushaf video generation from a "show-as-you-read" model to a persistent visibility model with dynamic highlighting.

## Phase 1: Implementation
- [x] Task: Modify `factories/single_clip.py` to ensure persistent visibility of text.
    - Update `generate_mushaf_page_clip` to always set the `duration` of the `ImageClip` (the text itself) to the full `duration` of the scene, regardless of `start_ms` and `end_ms`.
    - Ensure the `ColorClip` (the highlight block) remains timed to `start_ms` and `end_ms`.
- [x] Task: Verify that highlighting logic still excludes `surah_name` and `basmallah`.
- [x] Task: Conductor - User Manual Verification 'Visibility and Highlighting Fix' (Protocol in workflow.md)

## Phase 2: Verification
- [x] Task: Run `scripts/verify_mushaf_rendering.py` with Surah 108 to visually confirm:
    - All 15 lines (if on a full page) are visible from the first second.
    - Highlighting moves from line to line correctly.
    - Headers and Basmallah remain visible throughout the video.
