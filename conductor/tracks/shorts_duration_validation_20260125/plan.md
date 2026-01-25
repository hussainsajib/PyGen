# Plan: Duration Validation for YouTube Shorts

This plan outlines the steps to implement a duration check for Word-by-Word Shorts, ensuring they don't exceed the 60-second limit for YouTube uploads.

## Phase 1: Core Logic & Infrastructure [checkpoint: 0a968f7]
- [x] Task: Create a utility function to reliably retrieve the duration of an MP4 file. 623e2e0
    - [x] Write unit tests for the duration retrieval utility (e.g., tests/test_video_duration.py).
    - [x] Implement the utility using `moviepy` or `ffprobe`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Core Logic & Infrastructure' (Protocol in workflow.md) 0a968f7

## Phase 2: Workflow Integration [checkpoint: b13f243]
- [x] Task: Write integration tests for the WBW job workflow to verify the duration skip logic. 160178a
    - [x] Create tests that mock video generation with varied durations.
    - [x] Assert that YouTube upload is called for <= 60s and skipped for > 60s.
    - [x] Assert that Facebook upload is always called regardless of duration.
- [x] Task: Update `processes/processes.py` (or the relevant orchestration logic) to implement the check. 38056c4
    - [x] Modify the `create_wbw_video_job` (or equivalent) to retrieve duration post-generation.
    - [x] Add conditional logic to gate the `upload_to_youtube` call.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Workflow Integration' (Protocol in workflow.md) b13f243

## Phase 3: Feedback and Logging [checkpoint: 0d66e74]
- [x] Task: Implement informative logging for skipped uploads. a007900
    - [x] Add `logger.warning` or equivalent when a YouTube upload is skipped due to duration.
- [ ] Task: (Optional) Update the Job database model or metadata to store the reason for skip. (Skipped: Logging is sufficient)
- [x] Task: Conductor - User Manual Verification 'Phase 3: Feedback and Logging' (Protocol in workflow.md) 0d66e74

## Phase 4: Final Integration & Verification
- [ ] Task: Perform a comprehensive end-to-end manual verification.
    - [ ] Generate a short < 60s and verify dual upload.
    - [ ] Generate a short > 60s and verify only Facebook upload happens.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Integration & Verification' (Protocol in workflow.md)
