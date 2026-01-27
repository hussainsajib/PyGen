# Implementation Plan: Mushaf Surah Header Integration

This plan outlines the steps to integrate authentic Surah headers into the Mushaf video generator, ensuring they appear at the start of a Surah with correct styling and positioning.

## Phase 1: Research and Infrastructure
- [x] Task: Analyze `processes/mushaf_video.py` to identify the scene composition logic and where headers can be injected.
- [x] Task: Locate `QCF_SurahHeader_COLOR-Regular.ttf` in the codebase and verify its path (likely in `QPC_V2_Font.ttf/` or a similar assets directory).
- [x] Task: Create a mock Mushaf data provider/test case for a video starting at Ayah 1 of a Surah.

## Phase 2: Implementation
- [x] Task: Implement `SurahHeader` rendering logic in the Mushaf generation engine.
    - [x] Task: Update the line segmentation logic to reserve space for the header when starting at Ayah 1.
    - [x] Task: Implement a function to render the header text using the `QCF_SurahHeader_COLOR-Regular.ttf` font.
    - [x] Task: Adjust vertical positioning to ensure the header is centered at the top and doesn't overlap with Quranic lines.
- [x] Task: Synchronize header font size with the dynamically calculated size of the main Quranic text.
- [x] Task: Refine "Actual Mushaf" authenticity:
    - [x] Task: Use the single-glyph character `﷽` for `basmallah` lines.
    - [x] Task: Adjust scaling for `surah_name` and `basmallah` to `0.9` of line height for better visual fill.
    - [x] Task: Update injection logic in `mushaf_video.py` to also inject Bismillah if missing at start (except Surah 9).
    - [x] Task: Remove redundant Arial-based Bismillah overlay in `mushaf_video.py`.

## Phase 3: Integration and Verification
- [x] Task: Run `scripts/verify_mushaf_rendering.py` with a Surah starting at Ayah 1 to visually inspect the header.
- [x] Task: Verify that headers do *not* appear on subsequent pages of the same Surah.
- [x] Task: Conductor - User Manual Verification 'Mushaf Surah Header Integration' (Protocol in workflow.md)
