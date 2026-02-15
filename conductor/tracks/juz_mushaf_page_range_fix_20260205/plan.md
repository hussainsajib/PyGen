# Implementation Plan: Juz Mushaf Video Page Range & Audio Sync Fix

## Phase 1: Data Access & Boundary Logic [checkpoint: dece766]
Identify Surahs and Ayahs for a given Juz page range and calculate precise audio clipping points.

- [x] Task: Write unit tests for `get_ayahs_for_page_range` in `tests/test_mushaf_metadata.py`. [3c990a9]
- [x] Task: Implement `get_ayahs_for_page_range` in `db_ops/crud_mushaf.py` to query `mushaf_pages`. [3c990a9]
- [x] Task: Write unit tests for audio duration calculation based on word-level timestamps in `tests/test_juz_timing.py`. [4df691c]
- [x] Task: Update `prepare_juz_data_package` in `processes/mushaf_video.py` to accept `start_page` and `end_page` and clip data accordingly. [4df691c]
- [x] Task: Conductor - User Manual Verification 'Data Access & Boundary Logic' (Protocol in workflow.md)

## Phase 2: Asset Validation & Preparation [checkpoint: 7976366]
Ensure all fonts and images are ready before rendering.

- [x] Task: Write unit tests for `validate_mushaf_assets` in `tests/test_asset_validation.py`. [0996730]
- [x] Task: Implement `validate_mushaf_assets` to check for QPC v2 fonts and proactive image generation. [0996730]
- [x] Task: Update the `generate_juz_video` entry point to trigger validation and page generation before the main loop. [0996730]
- [x] Task: Conductor - User Manual Verification 'Asset Validation & Preparation' (Protocol in workflow.md)

## Phase 3: Video Engine Integration & Synchronization [checkpoint: faf2de5]
Update the rendering engine to respect page boundaries and ensure perfect sync.

- [x] Task: Write integration tests for page-clipped Juz video generation in `tests/test_juz_video_gen.py`. [10e776f]
- [x] Task: Refactor `generate_juz_video` loop to start and stop at the identified page boundaries. [3dd80b8]
- [x] Task: Verify word-level synchronization remains accurate after clipping the audio and timestamp streams. [3dd80b8]
- [x] Task: Conductor - User Manual Verification 'Video Engine Integration & Synchronization' (Protocol in workflow.md) [faf2de5]

## Phase 4: UI & API Integration
Expose the page range parameters to the frontend and job queue.

- [x] Task: Update the Juz video creation form in `templates/juz_video.html` to include optional "Start Page" and "End Page" inputs. [5671e11]
- [x] Task: Update the `/juz-video` route and `create_juz_video_job` to pass these parameters to the engine. [5671e11]
- [x] Task: Conductor - User Manual Verification 'UI & API Integration' (Protocol in workflow.md)
