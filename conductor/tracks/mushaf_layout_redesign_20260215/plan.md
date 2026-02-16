# Implementation Plan - Mushaf Video Layout Redesign

## Phase 1: Engine Refactoring (Fast Engine)
- [ ] Task: Create a reproduction script `repro_layout.py` using `MushafRenderer` to generate a single frame with the current layout for reference.
- [ ] Task: Modify `factories/mushaf_fast_render.py` (`_draw_overlays` method) to implement the new layout logic.
    - [ ] Remove existing footer drawing logic.
    - [ ] Implement `_draw_left_sidebar` to render the stacked Reciter/Surah/Brand text on the left.
    - [ ] Implement `_draw_right_sidebar` to render the Surah Header glyph on the right using `QCF_SurahHeader` font.
- [ ] Task: Run `repro_layout.py` to verify the new layout visually.
- [ ] Task: Conductor - User Manual Verification 'Engine Refactoring (Fast Engine)' (Protocol in workflow.md)

## Phase 2: Engine Refactoring (Standard Engine)
- [ ] Task: Modify `factories/single_clip.py` to support the new layout.
    - [ ] Update `generate_reciter_name_clip`, `generate_surah_info_clip`, and `generate_brand_clip` to position them in the left stack.
    - [ ] Create a new `generate_side_header_clip` function to render the Surah Header glyph.
    - [ ] Update `generate_mushaf_page_clip` to include these new sidebar elements instead of the footer.
- [ ] Task: Create a verification script `verify_standard_engine.py` to generate a short clip using `generate_mushaf_page_clip`.
- [ ] Task: Conductor - User Manual Verification 'Engine Refactoring (Standard Engine)' (Protocol in workflow.md)

## Phase 3: Global Configuration & Cleanup
- [ ] Task: Update `processes/video_configs.py` to define the new coordinate constants for Sidebars (Left/Right margins, vertical centering) and remove obsolete Footer configs.
- [ ] Task: Verify the changes by generating a full short video using `scripts/verify_boundary_refinement.py` (recycling the script or creating a new one).
- [ ] Task: Conductor - User Manual Verification 'Global Configuration & Cleanup' (Protocol in workflow.md)
