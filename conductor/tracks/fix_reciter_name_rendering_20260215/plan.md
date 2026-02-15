# Implementation Plan: Fix Reciter Name Rendering in Footer

## Phase 1: Investigation and Reproduction
- [ ] Task: Create a reproduction script `repro_footer_text.py` that renders a Bengali string using `PIL.ImageDraw` with `kalpurush.ttf` and saves the image.
- [ ] Task: Verify if the output image shows broken text.
- [ ] Task: Create a variant that uses `MoviePy.TextClip` (ImageMagick) to render the same string and compare.
- [ ] Task: Conductor - User Manual Verification 'Investigation and Reproduction' (Protocol in workflow.md)

## Phase 2: Implementation (Switch to Robust Rendering)
- [ ] Task: Identify if `MoviePy`'s `TextClip` produces correct output.
- [ ] Task: If so, refactor `MushafRenderer._draw_overlays` in `factories/mushaf_fast_render.py` to use a robust text rendering method (e.g., calling out to `TextClip` or a specialized Pango wrapper if available) instead of raw `PIL.ImageDraw` for complex scripts in the footer.
    - [ ] Create `render_complex_text_to_image(text, font_path, font_size, color)` utility.
    - [ ] Update `_draw_overlays` to use this utility and paste the result.
- [ ] Task: Ensure `factories/single_clip.py` (standard engine) also uses robust rendering for footer clips (`generate_reciter_name_clip`).
- [ ] Task: Conductor - User Manual Verification 'Implementation (Switch to Robust Rendering)' (Protocol in workflow.md)

## Phase 3: Verification
- [ ] Task: Generate a sample Mushaf video frame with the fix.
- [ ] Task: Verify visually that the Bengali text is joined and shaped correctly.
