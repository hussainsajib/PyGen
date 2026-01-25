# Plan: Duration Validation for YouTube Shorts

This plan outlines the steps to implement a duration check for Word-by-Word Shorts, ensuring they don't exceed the 60-second limit for YouTube uploads.

## Phase 1: Core Logic & Infrastructure
- [x] Task: Create a utility function to reliably retrieve the duration of an MP4 file. 623e2e0
    - [x] Write unit tests for the duration retrieval utility (e.g., tests/test_video_duration.py).
    - [x] Implement the utility using `moviepy` or `ffprobe`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Core Logic & Infrastructure' (Protocol in workflow.md)

## Phase 2: Workflow Integration
- [ ] Task: Write integration tests for the WBW job workflow to verify the duration skip logic.
    - [ ] Create tests that mock video generation with varied durations.
    - [ ] Assert that YouTube upload is called for <= 60s and skipped for > 60s.
    - [ ] Assert that Facebook upload is always called regardless of duration.
- [ ] Task: Update `processes/processes.py` (or the relevant orchestration logic) to implement the check.
    - [ ] Modify the `create_wbw_video_job` (or equivalent) to retrieve duration post-generation.
    - [ ] Add conditional logic to gate the `upload_to_youtube` call.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Workflow Integration' (Protocol in workflow.md)

## Phase 3: Feedback and Logging
- [ ] Task: Implement informative logging for skipped uploads.
    - [ ] Add `logger.warning` or equivalent when a YouTube upload is skipped due to duration.
- [ ] Task: (Optional) Update the Job database model or metadata to store the reason for skip.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Feedback and Logging' (Protocol in workflow.md)

## Phase 4: Final Integration & Verification
- [ ] Task: Perform a comprehensive end-to-end manual verification.
    - [ ] Generate a short < 60s and verify dual upload.
    - [ ] Generate a short > 60s and verify only Facebook upload happens.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Integration & Verification' (Protocol in workflow.md)
