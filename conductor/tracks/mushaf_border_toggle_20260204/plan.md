# Plan: Mushaf Video Border Toggle

## Phase 1: Configuration and UI [checkpoint: f5cb838]
- [x] Task: Add `MUSHAF_BORDER_ENABLED` to the default configuration in the database (default: "False"). d4dfc94
- [x] Task: Update `templates/config.html` to include a checkbox for `MUSHAF_BORDER_ENABLED`. 2d6a973
- [x] Task: Conductor - User Manual Verification 'Configuration and UI' (Protocol in workflow.md) f5cb838

## Phase 2: Implementation (TDD) [checkpoint: 0d1508d]
- [x] Task: Write failing unit tests in `tests/test_mushaf_border_toggle.py` to verify that border rendering is conditional based on the config. 313ead9
- [x] Task: Update `generate_mushaf_page_clip` in `factories/single_clip.py` to conditionally render the border. f3a1081
- [x] Task: Verify the tests pass. f3a1081
- [x] Task: Conductor - User Manual Verification 'Implementation (TDD)' (Protocol in workflow.md) 0d1508d

## Phase 3: Final Verification
- [ ] Task: Generate a sample Mushaf video with `MUSHAF_BORDER_ENABLED` set to "False" and verify the border is missing.
- [ ] Task: Generate a sample Mushaf video with `MUSHAF_BORDER_ENABLED` set to "True" and verify the border is present.
- [ ] Task: Conductor - User Manual Verification 'Final Verification' (Protocol in workflow.md)
