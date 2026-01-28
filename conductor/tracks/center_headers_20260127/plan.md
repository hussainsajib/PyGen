# Plan: Vertically Center Bismillah and Surah Header

## Phase 1: Research and Reproduction [checkpoint: 690d853]
- [x] Task: Identify the specific code responsible for drawing Bismillah and Surah Header text in Mushaf videos.
- [x] Task: Create a reproduction script/test that generates a frame with these headers for visual verification.
- [x] Task: Analyze current Y-coordinate calculations for these elements.
- [ ] Task: Conductor - User Manual Verification 'Research and Reproduction' (Protocol in workflow.md)

## Phase 2: Implementation (TDD) [checkpoint: e4001f4]
- [x] Task: Write failing unit tests for `calculate_vertical_center` or equivalent logic in the rendering module.
- [x] Task: Implement the vertical centering fix by adjusting the offset or baseline calculation.
- [x] Task: Verify the tests pass.
- [ ] Task: Conductor - User Manual Verification 'Implementation (TDD)' (Protocol in workflow.md)

## Phase 3: Integration and Final Verification [checkpoint: ]
- [ ] Task: Generate sample Mushaf video frames for Surah 1 and a Surah with a header (e.g., Surah 2) to confirm fixes.
- [ ] Task: Verify no regressions in text scaling or horizontal centering.
- [ ] Task: Conductor - User Manual Verification 'Integration and Final Verification' (Protocol in workflow.md)
