# Implementation Plan - Fix Missing Full Ayah Translation in WBW Videos

Fixing a regression where the full ayah translation is missing from word-by-word videos.

## Phase 1: Investigation and Environment Setup
- [ ] Task: Verify existing WBW rendering paths and identify where the translation overlay is skipped.
- [ ] Task: Ensure the testing environment has access to necessary translation databases (e.g., `rawai_al_bayan.sqlite`).
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Investigation and Environment Setup' (Protocol in workflow.md)

## Phase 2: Core Implementation
- [ ] Task: Update `processes/surah_video.py` to include full translation rendering in all WBW modes (Advanced, Standard, Interlinear).
    - [ ] Task: Write Tests: Create `tests/test_wbw_full_translation_rendering.py` to verify translation clip presence in composite clips.
    - [ ] Task: Implement: Ensure `create_ayah_clip`, `create_wbw_ayah_clip`, and `create_wbw_advanced_ayah_clip` correctly handle the translation overlay.
- [ ] Task: Refine styling in `factories/single_clip.py` by adding a semi-transparent background box to `generate_full_ayah_translation_clip`.
    - [ ] Task: Write Tests: Verify the background box is correctly added to the `CompositeVideoClip`.
    - [ ] Task: Implement: Add `ColorClip` as a background layer in `generate_full_ayah_translation_clip`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Core Implementation' (Protocol in workflow.md)

## Phase 3: Integration and Verification
- [ ] Task: Verify that the `WBW_FULL_TRANSLATION_SOURCE` configuration is correctly respected.
    - [ ] Task: Write Tests: Mock config to point to different translation sources and verify the correct text is fetched.
    - [ ] Task: Implement: Update `get_full_translation_for_ayah` calls to use the configured source.
- [ ] Task: Run end-to-end video generation tests for multiple reciters (e.g., Maher Al Muaiqly, Alafasy) to ensure visual consistency.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Integration and Verification' (Protocol in workflow.md)
