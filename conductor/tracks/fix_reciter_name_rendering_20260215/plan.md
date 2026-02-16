# Implementation Plan: Fix Reciter Name Rendering in Footer

## Phase 1: Investigation and Reproduction
- [x] Task: Create a reproduction script `repro_footer_text.py` that renders a Bengali string using `PIL.ImageDraw` with `kalpurush.ttf` and saves the image.
- [x] Task: Verify if the output image shows broken text.
- [x] Task: Create a variant that uses `MoviePy.TextClip` (ImageMagick) to render the same string and compare.
- [x] Task: Conductor - User Manual Verification 'Investigation and Reproduction' (Protocol in workflow.md)

## Phase 2: Implementation (Switch to Robust Rendering)
- [x] Task: Identify if `MoviePy`'s `TextClip` produces correct output.
- [x] Task: If so, refactor `MushafRenderer._draw_overlays` in `factories/mushaf_fast_render.py` to use a robust text rendering method (e.g., calling out to `TextClip` or a specialized Pango wrapper if available) instead of raw `PIL.ImageDraw` for complex scripts in the footer.
    - [x] Create `render_complex_text_to_image(text, font_path, font_size, color)` utility.
    - [x] Update `_draw_overlays` to use this utility and paste the result.
- [x] Task: Ensure `factories/single_clip.py` (standard engine) also uses robust rendering for footer clips (`generate_reciter_name_clip`).
- [x] Task: Conductor - User Manual Verification 'Implementation (Switch to Robust Rendering)' (Protocol in workflow.md)

## Phase 3: Verification
- [x] Task: Generate a sample Mushaf video frame with the fix.
- [x] Task: Verify visually that the Bengali text is joined and shaped correctly.
