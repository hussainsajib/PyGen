# Implementation Plan: Refined WBW YouTube Playlist Logic

## Phase 1: Frontend UI Updates [checkpoint: c413c53]
- [x] Task: Update playlist dropdown in WBW interface
    - [x] Sub-task: Modify `templates/wbw.html` to set "None (Upload Only)" as the default option with value `none`.
    - [x] Sub-task: Add "Reciter's Default Playlist" as an explicit option with value `default`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Frontend UI Updates' [c413c53] (Protocol in workflow.md)

## Phase 2: Backend Logic Implementation
- [ ] Task: Update WBW video job processing logic
    - [ ] Sub-task: Write failing tests for `create_wbw_video_job` handling `none` and `default` playlist options.
    - [ ] Sub-task: Update `create_wbw_video_job` in `processes/processes.py` to interpret `playlist_id='none'` as a instruction to skip playlist assignment.
    - [ ] Sub-task: Update `create_wbw_video_job` to interpret `playlist_id='default'` (or empty string if previously used) as a instruction to use the reciter's default playlist from the database.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Backend Logic Implementation' (Protocol in workflow.md)

## Phase 3: Integration and Final Verification
- [ ] Task: End-to-end verification of WBW upload behavior
    - [ ] Sub-task: Verify that selecting "None (Upload Only)" results in a video upload without a playlist.
    - [ ] Sub-task: Verify that selecting "Reciter's Default Playlist" results in an upload to the reciter's playlist.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Integration and Final Verification' (Protocol in workflow.md)
