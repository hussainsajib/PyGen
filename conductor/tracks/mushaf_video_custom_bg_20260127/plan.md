# Implementation Plan: Mushaf Video Customizable Page Background

This plan details the steps to implement configurable backgrounds for the internal Mushaf area and synchronize media selection between video types.

## Phase 1: Configuration & Engine Logic
- [~] Task: Define new configuration keys in the system.
    - Add `MUSHAF_PAGE_BACKGROUND_MODE` (Transparent, Semi-Transparent, Solid).
    - Add `MUSHAF_PAGE_BACKGROUND_COLOR` (Hex color string).
- [ ] Task: Update `factories/single_clip.py` to respect internal area settings.
    - Modify `generate_mushaf_border_clip` to use the new color and mode.
    - Implement opacity mapping: Transparent (0), Semi (128), Solid (255).
    - Disable noise texture unless mode is 'Solid'.
- [ ] Task: Write unit tests for rendering modes.
    - Create `tests/test_mushaf_background_modes.py`.
    - Verify the resulting `ImageClip` has the correct alpha channel properties for each mode.
- [ ] Task: Conductor - User Manual Verification 'Configuration & Engine Logic' (Protocol in workflow.md)

## Phase 2: User Interface Integration
- [x] Task: Update `templates/mushaf_video.html` UI.
    - Add the background selection modal (sharing logic with WBW).
    - Add a selection group for Background Mode and a Color Picker for the internal area.
- [x] Task: Update the global Configuration UI in `app.py` and `templates/config.html`.
    - Expose the new Mushaf background settings for global default management.
- [x] Task: Conductor - User Manual Verification 'User Interface Integration' (Protocol in workflow.md)

## Phase 3: Final Verification
- [x] Task: Run `scripts/verify_mushaf_rendering.py` with various background modes.
- [x] Task: Visually confirm that media assets (Unsplash/Pexels) are correctly displayed behind the text.
- [x] Task: Conductor - User Manual Verification 'Final Verification' (Protocol in workflow.md)
