# Implementation Plan: Enhanced WBW Rendering and YouTube Integration

## Phase 1: Configuration & UI Infrastructure
- [x] Task: Add configuration settings for full ayah translation
    - [x] Sub-task: Create a migration script to add `WBW_FULL_TRANSLATION_ENABLED` (default: false) and `WBW_FULL_TRANSLATION_SOURCE` (default: 'rawai_al_bayan') to the `config` table.
- [x] Task: Update Word-by-Word Interface for YouTube Settings
    - [x] Sub-task: Update the `/word-by-word` route in `app.py` to inject the global `UPLOAD_TO_YOUTUBE` flag and the list of available playlists (from the database) into the template context.
    - [x] Sub-task: Modify `templates/wbw.html` to include a "YouTube Settings" section with a checkbox for automatic upload and a dropdown for playlist selection.
- [x] Task: Convert WBW booleans to switches in Config UI
    - [x] Sub-task: Update `templates/config.html` to render `WBW_FULL_TRANSLATION_ENABLED` and `WBW_INTERLINEAR_ENABLED` as toggle switches instead of text inputs.
- [~] Task: Conductor - User Manual Verification 'Phase 1: Configuration & UI Infrastructure' (Protocol in workflow.md)

## Phase 2: Rendering Engine Enhancements
- [ ] Task: Adjust top-level metadata positioning
    - [ ] Sub-task: Update the rendering logic in `processes/surah_video.py` (or `factories/single_clip.py` as appropriate) to move the Reciter, Surah, and Brand info clips down by 50 pixels.
- [ ] Task: Implement full ayah translation overlay
    - [ ] Sub-task: Write failing tests for fetching and rendering the full ayah translation from the configurable source database.
    - [ ] Sub-task: Update `create_wbw_advanced_ayah_clip` in `processes/surah_video.py` to conditionally render the full translation at the bottom of the screen based on the `WBW_FULL_TRANSLATION_ENABLED` flag.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Rendering Engine Enhancements' (Protocol in workflow.md)

## Phase 3: YouTube Integration Backend
- [ ] Task: Update Job Management for WBW Uploads
    - [ ] Sub-task: Update the `enqueue_job` function and the job model to store YouTube upload preferences (auto-upload and playlist ID).
    - [ ] Sub-task: Modify `processes/processes.py` and the `job_worker` in `processes/background_worker.py` to trigger the YouTube upload specifically for WBW jobs when requested.
- [ ] Task: Integration Test for WBW YouTube Upload
    - [ ] Sub-task: Write failing integration tests to verify that a WBW job with the upload flag correctly initiates the YouTube upload to the specified playlist.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: YouTube Integration Backend' (Protocol in workflow.md)

## Phase 4: Final Integration & Verification
- [ ] Task: End-to-end verification of the enhanced WBW flow
    - [ ] Sub-task: Generate a WBW video with full translation enabled and automatic YouTube upload selected, then verify the final output and the upload status.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Integration & Verification' (Protocol in workflow.md)
