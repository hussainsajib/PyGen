# Implementation Plan: Mushaf Video Area Border

This plan details the steps to add a static decorative border around the Mushaf content area in generated videos.

## Phase 1: Implementation
- [x] Task: Modify `factories/single_clip.py` to create the border clip.
    - Implement a new helper function or logic inside `generate_mushaf_page_clip` to generate a `ColorClip` or use Pillow to draw a border with rounded corners.
    - Calculate the correct dimensions: `width * 0.95` (approx) and `usable_height` (from top_margin to bottom_margin).
- [x] Task: Integrate the border into the video composition.
    - Add the border clip to the `clips` list in `generate_mushaf_page_clip`.
    - Ensure it is placed behind the text but above the background.
- [x] Task: Conductor - User Manual Verification 'Mushaf Area Border' (Protocol in workflow.md)

## Phase 2: Verification
- [x] Task: Run `scripts/verify_mushaf_rendering.py` to visually confirm:
    - Border encompasses the entire Mushaf area.
    - Rounded corners and padding are correctly applied.
    - Static persistence throughout the clip.
