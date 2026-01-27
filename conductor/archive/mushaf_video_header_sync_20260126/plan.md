# Implementation Plan: Mushaf Video Header Sync

This plan details the steps to synchronize the video rendering of headers and Basmallah with the web viewer's aesthetic.

## Phase 1: Engine Refinement
- [x] Task: Update `generate_mushaf_page_clip` in `factories/single_clip.py`:
    - Refine `font_size` calculation for `surah_name` to match web proportions (~15% of width).
    - Ensure `basmallah` font size remains at the reduced scale (1.0x line_height).
    - Maintain auto-trimming and vertical centering logic.
- [x] Task: Add vertical margin after the Surah header by shifting its vertical position upward in the line slot.
- [x] Task: Conductor - User Manual Verification 'Engine Refinement' (Protocol in workflow.md)

## Phase 2: Verification
- [ ] Task: Run `scripts/verify_mushaf_rendering.py` to generate sample videos.
- [ ] Task: Visually confirm parity with the web viewer for Page 1 and Page 2.
