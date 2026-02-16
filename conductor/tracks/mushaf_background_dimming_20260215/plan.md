# Implementation Plan - Background Dimming & Footer Cleanup

## Phase 1: Core Logic & Fast Engine
- [x] Task: Update `factories/mushaf_fast_render.py` (`_draw_overlays` method). [checkpoint: b9cb8a2]
    - [x] Remove the PIL code responsible for drawing the semi-transparent footer background bar.
    - [x] Implement the background dimming by drawing a full-screen semi-transparent black rectangle over the background image *before* other elements are pasted.
- [x] Task: Update `MushafRenderer` to retrieve the `MUSHAF_BACKGROUND_DIMMING` setting via `config_manager`.
- [x] Task: Create a verification script `verify_fast_dimming.py` using `MushafRenderer` to save a frame with 50% dimming and no footer bar.
- [x] Task: Conductor - User Manual Verification 'Core Logic & Fast Engine' (Protocol in workflow.md) [checkpoint: 425cff8]

## Phase 2: Standard Engine & Config
- [x] Task: Update `factories/single_clip.py`. [checkpoint: 3f2df18]
    - [x] Update `generate_background` to accept a `dimming` parameter and layer a `ColorClip(color=(0,0,0))` over the background asset.
    - [x] Update `generate_mushaf_page_clip` to remove the `generate_footer_bar_clip` call and the corresponding overlay assembly.
- [x] Task: Update `processes/mushaf_video.py` to pass the dimming value to the background generator.
- [x] Task: Update the web configuration template (`templates/config.html` or similar) to include the `MUSHAF_BACKGROUND_DIMMING` setting.
- [x] Task: Conductor - User Manual Verification 'Standard Engine & Config' (Protocol in workflow.md) [checkpoint: e18f037]

## Phase 3: Final Verification
- [x] Task: Generate a full video segment for a Juz using the Fast Engine and verify the darkened background and clean footer visually.
- [x] Task: Synchronize `conductor/product.md` to reflect the new dimming capabilities and refined footer.
- [x] Task: Conductor - User Manual Verification 'Final Verification' (Protocol in workflow.md) [checkpoint: a6e1d54]
