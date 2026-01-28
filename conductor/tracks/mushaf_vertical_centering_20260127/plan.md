# Plan: Mushaf Video Vertical Centering and Spacing

## Phase 1: Research and Math Verification [checkpoint: db709a4]
- [x] Task: Identify the current calculation logic for `top_margin`, `line_height`, and individual line positioning in `generate_mushaf_page_clip`.
- [x] Task: Determine the effective "content height" for different scenarios (full page, partial page).
- [ ] Task: Conductor - User Manual Verification 'Research and Math Verification' (Protocol in workflow.md)

## Phase 2: Implementation (TDD) [checkpoint: 9c0db3a]
- [x] Task: Write failing unit tests for the vertical centering calculation (mocking screen height and content height).
- [x] Task: Implement the dynamic vertical centering logic in `generate_mushaf_page_clip`.
- [x] Task: Implement the specific +20px gap between the Surah Header and Bismillah.
- [x] Task: Verify the tests pass and handle potential edge cases (e.g., extremely long pages that shouldn't move).
- [ ] Task: Conductor - User Manual Verification 'Implementation (TDD)' (Protocol in workflow.md)

## Phase 3: Integration and Final Verification [checkpoint: ]
- [x] Task: Generate sample frames for a full Mushaf page and a partial page (end of Surah).
- [x] Task: Verify visual centering and header spacing in both portrait (Shorts) and landscape formats.
- [x] Task: Conductor - User Manual Verification 'Integration and Final Verification' (Protocol in workflow.md)
