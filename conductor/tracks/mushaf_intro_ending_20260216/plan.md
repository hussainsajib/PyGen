# Implementation Plan - Intro and Ending Screens for Mushaf Videos

## Phase 1: Shared Rendering Logic & Fast Engine Core
- [ ] Task: Update `factories/mushaf_fast_render.py` to support full-screen text overlays.
    - [ ] Enhance `MushafRenderer` to handle `intro` and `ending` rendering modes.
    - [ ] Implement `_draw_intro_screen` to render Surah/Para name and Reciter centered in Bengali.
    - [ ] Implement `_draw_ending_screen` to render "তাকওয়া বাংলা" and subscribe CTA.
    - [ ] Ensure `MUSHAF_BACKGROUND_DIMMING` is applied to these screens.
- [ ] Task: Write failing unit tests in `tests/test_intro_ending_layout.py`.
    - [ ] Mock a renderer and verify that text elements are centered and correctly localized.
- [ ] Task: Conductor - User Manual Verification 'Shared Rendering Logic & Fast Engine Core' (Protocol in workflow.md)

## Phase 2: High-Speed Sequence Integration
- [ ] Task: Update `processes/mushaf_fast_video.py`.
    - [ ] Update `generate_mushaf_fast` to prepend a 5-second intro and append a 5-second ending to the scene list.
    - [ ] Shift all main recitation timestamps by 5 seconds to account for the intro.
    - [ ] Update `total_duration` calculation to include the additional 10 seconds.
- [ ] Task: Verify that the progress bar correctly handles the new total duration.
- [ ] Task: Conductor - User Manual Verification 'High-Speed Sequence Integration' (Protocol in workflow.md)

## Phase 3: Standard Engine Integration
- [ ] Task: Update `processes/mushaf_video.py`.
    - [ ] Update `generate_mushaf_video` and `generate_juz_video` to generate intro and ending clips.
    - [ ] Prepend/append these clips to the final `concatenate_videoclips` call.
    - [ ] Ensure audio tracks are correctly aligned (silence during intro/ending unless music is added later).
- [ ] Task: Conductor - User Manual Verification 'Standard Engine Integration' (Protocol in workflow.md)

## Phase 4: Final Verification & Documentation
- [ ] Task: Generate a short Mushaf video (e.g., Surah 108) using the FFmpeg engine and verify the intro/ending visually.
- [ ] Task: Synchronize `conductor/product.md` to include Intro/Ending screens as a standard feature.
- [ ] Task: Conductor - User Manual Verification 'Final Verification & Documentation' (Protocol in workflow.md)
