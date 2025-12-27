# Implementation Plan: Enhanced WBW Rendering and YouTube Integration

## Phase 1: Configuration & UI Infrastructure [checkpoint: 2d77e60]
- [x] Task: Add configuration settings for full ayah translation
    - [x] Sub-task: Create a migration script to add `WBW_FULL_TRANSLATION_ENABLED` (default: false) and `WBW_FULL_TRANSLATION_SOURCE` (default: 'rawai_al_bayan') to the `config` table.
- [x] Task: Update Word-by-Word Interface for YouTube Settings
    - [x] Sub-task: Update the `/word-by-word` route in `app.py` to inject the global `UPLOAD_TO_YOUTUBE` flag and the list of available playlists (from the database) into the template context.
    - [x] Sub-task: Modify `templates/wbw.html` to include a "YouTube Settings" section with a checkbox for automatic upload and a dropdown for playlist selection.
- [x] Task: Remove redundant upload toggle from WBW UI
    - [x] Sub-task: Update `templates/wbw.html` to show playlist selection directly without the extra toggle.
    - [x] Sub-task: Update `app.py` to implicitly set upload preference based on global config.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Configuration & UI Infrastructure' [2d77e60] (Protocol in workflow.md)

## Phase 2: Rendering Engine Enhancements [checkpoint: 5b65ae9]
- [x] Task: Adjust top-level metadata positioning
    - [x] Sub-task: Update the rendering logic in `processes/surah_video.py` (or `factories/single_clip.py` as appropriate) to move the Reciter, Surah, and Brand info clips down by 50 pixels.
- [x] Task: Implement full ayah translation overlay
    - [x] Sub-task: Write failing tests for fetching and rendering the full ayah translation from the configurable source database.
    - [x] Sub-task: Update `create_wbw_advanced_ayah_clip` in `processes/surah_video.py` to conditionally render the full translation at the bottom of the screen based on the `WBW_FULL_TRANSLATION_ENABLED` flag.
- [x] Task: Make full translation font size configurable
    - [x] Sub-task: Add `WBW_FULL_TRANSLATION_FONT_SIZE` (default: 30) to the `config` table.
    - [x] Sub-task: Update `factories/single_clip.py` to use this configuration value when rendering the overlay.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Rendering Engine Enhancements' [5b65ae9] (Protocol in workflow.md)

## Phase 3: YouTube Integration Backend [checkpoint: fab6ab2]
- [x] Task: Update Job Management for WBW Uploads
    - [x] Sub-task: Update the `enqueue_job` function and the job model to store YouTube upload preferences (auto-upload and playlist ID).
    - [x] Sub-task: Modify `processes/processes.py` and the `job_worker` in `processes/background_worker.py` to trigger the YouTube upload specifically for WBW jobs when requested.
- [x] Task: Integration Test for WBW YouTube Upload
    - [x] Sub-task: Write failing integration tests to verify that a WBW job with the upload flag correctly initiates the YouTube upload to the specified playlist.
- [x] Task: Conductor - User Manual Verification 'Phase 3: YouTube Integration Backend' [fab6ab2] (Protocol in workflow.md)

## Phase 4: Final Integration & Verification [checkpoint: 96b48b7]
- [x] Task: End-to-end verification of the enhanced WBW flow
    - [x] Sub-task: Generate a WBW video with full translation enabled and automatic YouTube upload selected, then verify the final output and the upload status.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Final Integration & Verification' [96b48b7] (Protocol in workflow.md)
