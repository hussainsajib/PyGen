# Implementation Plan - Revert Metadata Layout to Footer with Bar

## Phase 1: Engine Refactoring (Fast Engine)
- [ ] Task: Create a reproduction script `repro_footer_bar.py` using `MushafRenderer` to generate a single frame for testing.
- [ ] Task: Update `factories/mushaf_fast_render.py` (`_draw_overlays` method).
    - [ ] Remove sidebar stacking logic.
    - [ ] Implement drawing of the semi-transparent footer background bar using PIL `ImageDraw`.
    - [ ] Re-implement horizontal positioning for Reciter (left), Surah (center), and Brand (right) within the bar area.
- [ ] Task: Run `repro_footer_bar.py` to verify the new footer layout visually.
- [ ] Task: Conductor - User Manual Verification 'Engine Refactoring (Fast Engine)' (Protocol in workflow.md)

## Phase 2: Engine Refactoring (Standard Engine)
- [ ] Task: Update `factories/single_clip.py`.
    - [ ] Remove `generate_metadata_sidebar` logic.
    - [ ] Create a new `generate_footer_bar_clip` function that returns a semi-transparent `ColorClip` or `ImageClip`.
    - [ ] Re-implement individual metadata clip generation and horizontal positioning.
    - [ ] Update `generate_mushaf_page_clip` to assemble the new footer bar and text overlays.
- [ ] Task: Create a verification script `verify_footer_standard.py` to generate a frame using the MoviePy engine.
- [ ] Task: Conductor - User Manual Verification 'Engine Refactoring (Standard Engine)' (Protocol in workflow.md)

## Phase 3: Configuration & Synchronization
- [ ] Task: Update `processes/video_configs.py`.
    - [ ] Redefine footer position constants/functions.
    - [ ] Add configuration for footer bar height and opacity.
- [ ] Task: Synchronize `conductor/product.md` to reflect the return to the enhanced footer layout.
- [ ] Task: Conductor - User Manual Verification 'Configuration & Synchronization' (Protocol in workflow.md)
