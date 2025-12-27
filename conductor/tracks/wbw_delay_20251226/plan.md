# Implementation Plan: Configurable Delay between WBW Ayah Clips

## Phase 1: Configuration Infrastructure
- [x] Task: Add delay configuration to database
    - [x] Sub-task: Create a migration script to add `WBW_DELAY_BETWEEN_AYAH` with a default of 0.5 to the `config` table.
- [x] Task: Verify configuration in UI
    - [x] Sub-task: Manually confirm the new key appears in the `/config` dashboard.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Configuration Infrastructure' (Protocol in workflow.md)

## Phase 2: Engine Implementation
- [x] Task: Modify WBW clip generation logic
    - [x] Sub-task: Write failing test for clip duration extension with silent gap.
    - [x] Sub-task: Update `create_wbw_advanced_ayah_clip` in `processes/surah_video.py` to fetch the delay and append the silent/extended-frame segment.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Engine Implementation' (Protocol in workflow.md)

## Phase 3: Integration and Testing [checkpoint: 9ecf503]
- [x] Task: Full-Surah Generation Test
    - [x] Sub-task: Write failing test for `generate_surah` ensuring total duration includes the aggregated delays.
    - [x] Sub-task: Verify WBW video generation includes the pauses while standard generation remains the same.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Integration and Testing' [594ed84] (Protocol in workflow.md)
