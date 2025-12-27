# Implementation Plan: Dynamic and Standardized Threading for Video Encoding

## Phase 1: Configuration Infrastructure [checkpoint: 71c1864]
- [x] Task: Centralize threading configuration [7a47f12]
    - [x] Sub-task: Update `processes/video_configs.py` to calculate `VIDEO_ENCODING_THREADS` dynamically using `os.cpu_count() - 1`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Configuration Infrastructure' (Protocol in workflow.md)

## Phase 2: Engine Refactoring [checkpoint: 825d1e5]
- [x] Task: Refactor Surah Video Generation [f6193ee]
    - [x] Sub-task: Write a test to verify `generate_surah` uses the configured thread count (mocking `write_videofile`).
    - [x] Sub-task: Update `processes/surah_video.py` to use `VIDEO_ENCODING_THREADS`.
- [x] Task: Refactor Word-by-Word Video Generation [dc2a707]
    - [x] Sub-task: Write a test to verify `generate_video` uses the configured thread count (mocking `write_videofile`).
    - [x] Sub-task: Update `processes/video_utils.py` to use `VIDEO_ENCODING_THREADS`.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Engine Refactoring' (Protocol in workflow.md)

## Phase 3: Integration and Verification
- [x] Task: Verification
    - [x] Sub-task: Run all tests to ensure no regressions in video generation.
    - [x] Sub-task: Manually trigger a short video generation to confirm it completes successfully.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Integration and Verification' (Protocol in workflow.md)
