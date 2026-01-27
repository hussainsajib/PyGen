# Implementation Plan: Authentic Mushaf Video Border

This plan details the steps to upgrade the Mushaf area border into a multi-layered, textured "book" frame.

## Phase 1: Engine Enhancement
- [x] Task: Update `generate_mushaf_border_clip` in `factories/single_clip.py`.
    - Modify the function to draw two concentric rounded rectangles (Outer: thick, Inner: thin).
    - Ensure the width is fixed (e.g., `width * 0.90`).
- [x] Task: Implement texture logic.
    - Create or source a subtle grain texture.
    - Update `generate_mushaf_border_clip` to fill the inner rectangle with a textured cream background.
- [x] Task: Conductor - User Manual Verification 'Authentic Border' (Protocol in workflow.md)

## Phase 2: Verification
- [x] Task: Run `scripts/verify_mushaf_rendering.py` to visually confirm:
    - Double border styling.
    - Paper texture presence.
    - Consistent fixed width across different page types.
