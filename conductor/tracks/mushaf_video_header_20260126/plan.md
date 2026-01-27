# Implementation Plan: Mushaf Video Header and Basmallah Integration

This plan details the steps to synchronize the Mushaf video generation engine with the authentic rendering logic used in the `/mushaf` viewer, including decorative headers and timed Basmallah rendering.

## Phase 1: Preparation and Testing
- [x] Task: Analyze `processes/mushaf_video.py` and `factories/single_clip.py` to identify the best injection points for the new rendering logic.
- [x] Task: Create a failing unit test in `tests/test_mushaf_video_headers.py` that asserts the presence of header and Basmallah clips in the first scene of a Mushaf video.
- [x] Task: Ensure `databases/text/ligatures.json` is accessible to the video generation process.
- [x] Task: Conductor - User Manual Verification 'Preparation and Testing' (Protocol in workflow.md)

## Phase 2: Engine Implementation
- [x] Task: Update `generate_mushaf_page_clip` in `factories/single_clip.py`:
    - Implement rendering for `line_type: surah_name` using `QCF_SurahHeader_COLOR-Regular.ttf` and ligatures.
    - Implement rendering for `line_type: basmallah` using `QCF_BSML.TTF` and character `U+00F3`.
    - Apply auto-trimming and precise centering logic developed for the web viewer.
- [x] Task: Update `generate_mushaf_video` in `processes/mushaf_video.py`:
    - Inject the Surah header and Basmallah lines into the initial line list if Ayah 1 is present.
    - Implement visibility timing logic: set the duration of these clips to match only the first recitation segment (Ayah 1 or Bismillah).
    - Ensure these elements are positioned at the very top of the composite scene.
- [x] Task: Conductor - User Manual Verification 'Engine Implementation' (Protocol in workflow.md)

## Phase 3: Verification and Polishing
- [x] Task: Run `scripts/verify_mushaf_rendering.py` with a Surah start case to generate a sample video for visual inspection.
- [x] Task: Verify that headers/Basmallah correctly disappear after the first Ayah is recited.
- [x] Task: Perform a regression test on existing Mushaf video generation to ensure no layout shifts or timing issues for ongoing pages.
- [x] Task: Conductor - User Manual Verification 'Integration and Verification' (Protocol in workflow.md)
