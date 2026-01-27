# Implementation Plan: Mushaf Video Dynamic Highlighting Width

This plan details the changes to `factories/single_clip.py` to implement line-width-aware highlighting in Mushaf videos.

## Phase 1: Implementation
- [x] Task: Modify `factories/single_clip.py` to calculate dynamic highlight width.
    - Inside `generate_mushaf_page_clip`, capture the `width` of the `img_array` (the trimmed text image).
    - Update the `ColorClip` creation to use `size=(img_array.shape[1] + 20, int(line_height))` instead of a fixed 95% width.
    - Ensure the `ColorClip` position remains centered horizontally using `set_position(('center', y_pos))`.
- [x] Task: Conductor - User Manual Verification 'Dynamic Highlighting Width' (Protocol in workflow.md)

## Phase 2: Verification
- [x] Task: Run `scripts/verify_mushaf_rendering.py` to visually confirm:
    - Highlight width matches the text width for short and long lines.
    - Highlight remains correctly aligned vertically.
