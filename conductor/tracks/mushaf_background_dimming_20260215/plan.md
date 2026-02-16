# Implementation Plan - Background Dimming & Footer Cleanup

## Phase 1: Core Logic & Fast Engine
- [ ] Task: Update `factories/mushaf_fast_render.py` (`_draw_overlays` method).
    - [ ] Remove the PIL code responsible for drawing the semi-transparent footer background bar.
    - [ ] Implement the background dimming by drawing a full-screen semi-transparent black rectangle over the background image *before* other elements are pasted.
- [ ] Task: Update `MushafRenderer` to retrieve the `MUSHAF_BACKGROUND_DIMMING` setting via `config_manager`.
- [ ] Task: Create a verification script `verify_fast_dimming.py` using `MushafRenderer` to save a frame with 50% dimming and no footer bar.
- [ ] Task: Conductor - User Manual Verification 'Core Logic & Fast Engine' (Protocol in workflow.md)

## Phase 2: Standard Engine & Config
- [ ] Task: Update `factories/single_clip.py`.
    - [ ] Update `generate_background` to accept a `dimming` parameter and layer a `ColorClip(color=(0,0,0))` over the background asset.
    - [ ] Update `generate_mushaf_page_clip` to remove the `generate_footer_bar_clip` call and the corresponding overlay assembly.
- [ ] Task: Update `processes/mushaf_video.py` to pass the dimming value to the background generator.
- [ ] Task: Update the web configuration template (`templates/config.html` or similar) to include the `MUSHAF_BACKGROUND_DIMMING` setting.
- [ ] Task: Conductor - User Manual Verification 'Standard Engine & Config' (Protocol in workflow.md)

## Phase 3: Final Verification
- [ ] Task: Generate a full video segment for a Juz using the Fast Engine and verify the darkened background and clean footer visually.
- [ ] Task: Synchronize `conductor/product.md` to reflect the new dimming capabilities and refined footer.
- [ ] Task: Conductor - User Manual Verification 'Final Verification' (Protocol in workflow.md)
