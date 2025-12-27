# Implementation Plan: Word-by-Word Interlinear Rendering

## Phase 1: Configuration Infrastructure [checkpoint: 888bd7a]
- [x] Task: Add configuration settings for interlinear rendering [04af142]
    - [x] Sub-task: Create a migration script to add `WBW_INTERLINEAR_ENABLED` (default: false) and `WBW_TRANSLATION_FONT_SIZE` (default: 20) to the `config` table.
    - [x] Sub-task: Verify the new settings appear and are editable in the `/config` dashboard.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Configuration Infrastructure' (Protocol in workflow.md)

## Phase 2: Engine Logic & Segmentation
- [x] Task: Update word segmentation to account for interlinear widths [a521093]
    - [x] Sub-task: Write failing tests for word width calculation that considers both the Arabic word and its translation.
    - [x] Sub-task: Modify `processes/wbw_utils.py` to calculate block widths based on the wider of the two elements (Arabic word or translation).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Engine Logic & Segmentation' (Protocol in workflow.md)
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Engine Logic & Segmentation' (Protocol in workflow.md)

## Phase 3: Rendering Implementation
- [ ] Task: Implement interlinear text clip generation
    - [ ] Sub-task: Write failing tests for the interlinear rendering (validating correct centering and the presence of an underline).
    - [ ] Sub-task: Update `factories/single_clip.py` to implement `generate_wbw_interlinear_text_clip`. This will use Pillow to draw the Arabic word, a solid underline, and the translation text centered directly below.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Rendering Implementation' (Protocol in workflow.md)

## Phase 4: Integration and Verification
- [ ] Task: Integrate interlinear rendering into the video generation process
    - [ ] Sub-task: Update `processes/surah_video.py` to trigger the interlinear rendering path when `WBW_INTERLINEAR_ENABLED` is true.
    - [ ] Sub-task: Verify that highlighting remains synchronized with the new layout during video generation.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Integration and Verification' (Protocol in workflow.md)
