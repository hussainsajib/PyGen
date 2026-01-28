# Plan: Mushaf Video Text Scaling Refinement

## Phase 1: Configuration and UI [checkpoint: 1de40dd]
- [x] Task: Add `MUSHAF_FONT_SCALE` to the default configuration set in the database (default: 0.8).
- [x] Task: Update `templates/config.html` to include a numerical input field for `MUSHAF_FONT_SCALE`.
- [ ] Task: Conductor - User Manual Verification 'Configuration and UI' (Protocol in workflow.md)

## Phase 2: Implementation (TDD) [checkpoint: 5ea53dc]
- [x] Task: Write failing unit tests for the font size calculation logic in `factories/single_clip.py` to ensure the scaling factor is applied.
- [x] Task: Implement the `MUSHAF_FONT_SCALE` multiplier in the `generate_mushaf_page_clip` function.
- [x] Task: Verify the tests pass.
- [ ] Task: Conductor - User Manual Verification 'Implementation (TDD)' (Protocol in workflow.md)

## Phase 3: Final Verification [checkpoint: ]
- [ ] Task: Generate a sample Mushaf video frame and compare the Ayah text size with a previous version (or calculate visual pixel height).
- [ ] Task: Confirm that vertical centering remains accurate with the smaller font.
- [ ] Task: Conductor - User Manual Verification 'Final Verification' (Protocol in workflow.md)
