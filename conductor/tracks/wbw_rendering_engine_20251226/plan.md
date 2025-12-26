# Implementation Plan: Advanced Word-by-Word Rendering Engine

## Phase 1: Database and Model Infrastructure [checkpoint: d811509]
- [x] Task: Implement CRUD for WBW Text and Translation
    - [x] Sub-task: Write failing tests for fetching words from `qpc-hafs-word-by-word.db` and translations from `bangali-word-by-word-translation.sqlite`.
    - [x] Sub-task: Implement `get_wbw_text_for_ayah` and `get_wbw_translation_for_ayah` in `db_ops/crud_wbw.py` (or new dedicated file).
- [x] Task: Configure WBW Font Sizes
    - [x] Sub-task: Add default `WBW_FONT_SIZE_REGULAR` and `WBW_FONT_SIZE_SHORT` entries to the configuration system via a script.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Database and Model Infrastructure' (Protocol in workflow.md)

## Phase 2: Core Segmentation Logic
- [ ] Task: Implement Word-to-Line Segmentation Utility
    - [ ] Sub-task: Write failing tests for the segmentation logic (character count, soft limit, resolution awareness).
    - [ ] Sub-task: Create `processes/wbw_utils.py` with `segment_words_into_lines` function.
- [ ] Task: Integrate Timestamps with Segments
    - [ ] Sub-task: Write failing tests for collective time aggregation (mapping word durations to line durations).
    - [ ] Sub-task: Implement logic to calculate start/end times for each line based on aggregated individual word segments.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Core Segmentation Logic' (Protocol in workflow.md)

## Phase 3: Video Engine Integration
- [ ] Task: Implement Multi-Line Rendering in Clip Generation
    - [ ] Sub-task: Write failing tests for generating an ayah clip with segmented WBW lines.
    - [ ] Sub-task: Update `processes/surah_video.py` to handle the new line-based rendering workflow.
    - [ ] Sub-task: Update `factories/single_clip.py` to support rendering grouped segments with configurable font sizes and layout.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Video Engine Integration' (Protocol in workflow.md)
