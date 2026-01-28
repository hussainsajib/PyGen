# Plan: Mushaf Video Layered Background Refinement

## Phase 1: Configuration and Renaming [checkpoint: 7ca0f1b]
- [x] Task: Perform a global find-and-replace for `MUSHAF_PAGE_BACKGROUND_COLOR` to `MUSHAF_PAGE_COLOR`.
- [x] Task: Add `MUSHAF_PAGE_OPACITY` to the default configuration (e.g., in `config_manager.py` or initial setup).
- [x] Task: Update the frontend configuration UI to include the `MUSHAF_PAGE_OPACITY` slider (0-100).
- [x] Task: Update the frontend configuration UI to reflect the renamed `MUSHAF_PAGE_COLOR` field.
- [ ] Task: Conductor - User Manual Verification 'Configuration and Renaming' (Protocol in workflow.md)

## Phase 2: Backend Rendering Refactor (TDD) [checkpoint: 2e2174a]
- [x] Task: Write unit tests for the updated background selection logic (ACTIVE_BACKGROUND vs BACKGROUND_RGB).
- [x] Task: Write unit tests for the inner page fill calculation (Transparent, Semi, Solid).
- [x] Task: Modify `generate_mushaf_border_clip` in `factories/single_clip.py` to handle transparency and opacity in its inner fill.
- [x] Task: Modify `generate_mushaf_page_clip` in `factories/single_clip.py` to correctly layer the global background (image/video/RGB) beneath the border and page content.
- [x] Task: Verify all tests pass and handle edge cases (e.g., missing assets, invalid hex codes).
- [ ] Task: Conductor - User Manual Verification 'Backend Rendering Refactor (TDD)' (Protocol in workflow.md)

## Phase 3: Integration and Final Verification [checkpoint: 6ccd9aa]
- [x] Task: Generate sample Mushaf video frames for all three modes: Transparent, Semi (with varying opacity), and Solid.
- [x] Task: Verify that `ACTIVE_BACKGROUND` is correctly prioritized over `BACKGROUND_RGB` for the outer area.
- [x] Task: Ensure the UI slider correctly updates the configuration and affects the rendered output.
- [x] Task: Conductor - User Manual Verification 'Integration and Final Verification' (Protocol in workflow.md)
