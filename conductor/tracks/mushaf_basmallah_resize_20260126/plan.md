# Implementation Plan: Mushaf Basmallah Resize

This plan covers the adjustment of Basmallah font scaling in Mushaf videos to synchronize its appearance with the web viewer.

## Phase 1: Implementation
- [x] Task: Modify `factories/single_clip.py` to use a specific scaling factor for `basmallah` lines.
    - Change `font_size` calculation to use `line_height * 1.3` for Basmallah (matching the web ratio of ~1.9x standard text).
- [x] Task: Conductor - User Manual Verification 'Basmallah Resize' (Protocol in workflow.md)

## Phase 2: Verification
- [x] Task: Run `scripts/verify_mushaf_rendering.py` to generate a sample video.
- [x] Task: Visually confirm the Basmallah is now smaller and matches the web proportions.
