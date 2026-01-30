# Plan: Mushaf Video Configurable Border Width

## Phase 1: Configuration and UI [checkpoint: 166b91d]
- [x] Task: Add `MUSHAF_BORDER_WIDTH_PERCENT` to the default configuration in the database (default: 40).
- [x] Task: Update `templates/config.html` to include a range slider for `MUSHAF_BORDER_WIDTH_PERCENT` (10-90).
- [ ] Task: Conductor - User Manual Verification 'Configuration and UI' (Protocol in workflow.md)

## Phase 2: Implementation (TDD) [checkpoint: c24c901]
- [x] Task: Write failing unit tests for the border width calculation logic in `factories/single_clip.py`. c23015d
- [x] Task: Refactor `generate_mushaf_page_clip` to use the dynamic `MUSHAF_BORDER_WIDTH_PERCENT` value. b10d7db
- [x] Task: Verify the tests pass. c23015d
- [x] Task: Conductor - User Manual Verification 'Implementation (TDD)' (Protocol in workflow.md) c24c901

## Phase 3: Final Verification [checkpoint: 3e7db10]
- [x] Task: Generate sample frames with different border width settings (e.g., 20, 40, 60) to verify visual changes. 3e7db10
- [x] Task: Confirm that the default setting (40) results in the expected narrower appearance. 3e7db10
- [x] Task: Conductor - User Manual Verification 'Final Verification' (Protocol in workflow.md) 3e7db10
