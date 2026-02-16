# Implementation Plan - Fix Incorrect Start Page for Juz Video Basmallah

## Phase 1: Investigation and Reproduction
- [ ] Task: Analyze page number assignment in `processes/mushaf_video.py` and `processes/mushaf_fast_video.py` for Juz videos.
    - [ ] Review how the first scene's `page_num` is determined during Basmallah injection.
- [ ] Task: Create a reproduction script `reproduce_juz_bug.py` to verify the issue.
    - [ ] Generate a single frame for the start of Juz 2.
    - [ ] Assert that it currently shows the wrong page (e.g., Page 2 instead of Page 22).
- [ ] Task: Conductor - User Manual Verification 'Investigation and Reproduction' (Protocol in workflow.md)

## Phase 2: Implementation (Standard Engine)
- [ ] Task: Write failing unit tests in `tests/test_juz_start_page.py`.
    - [ ] Mock boundaries and check aligned lines for correct page numbers.
- [ ] Task: Update `processes/mushaf_video.py` to fix the start page logic.
    - [ ] Ensure the first injected Basmallah segment uses the Juz start page from boundaries.
- [ ] Task: Verify fix with tests and reproduction script.
- [ ] Task: Conductor - User Manual Verification 'Implementation (Standard Engine)' (Protocol in workflow.md)

## Phase 3: Implementation (Fast Engine)
- [ ] Task: Write failing unit tests for the Fast Engine path.
- [ ] Task: Update `processes/mushaf_fast_video.py` to ensure consistency.
    - [ ] Fix the `page_num` assignment for the initial scene in high-speed rendering.
- [ ] Task: Verify fix with tests and reproduction script.
- [ ] Task: Conductor - User Manual Verification 'Implementation (Fast Engine)' (Protocol in workflow.md)

## Phase 4: Final Verification and Documentation
- [ ] Task: Perform a full visual check by generating a short video snippet for Juz 2.
- [ ] Task: Synchronize project documentation if any logic changes impact the Product Definition.
- [ ] Task: Conductor - User Manual Verification 'Final Verification and Documentation' (Protocol in workflow.md)
