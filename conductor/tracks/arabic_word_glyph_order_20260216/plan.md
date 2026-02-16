# Implementation Plan - Fix Arabic Word Ordering in Fast Engines

## Phase 1: Investigation & Reproduction
- [x] Task: Create a reproduction script `reproduce_alignment_issue.py` that uses `MushafRenderer` to render a single line and saves it as an image. [checkpoint: b370060]
    - [x] Target a known multi-word line (e.g., Surah 2, Ayah 1).
    - [x] Verify that the words are currently swapped or LTR.
- [x] Task: Analyze `factories/mushaf_fast_render.py` (`_prepare_renderable_lines` and `prepare_static_base`). [checkpoint: b370060]
    - [x] Check if `reversed()` is being used incorrectly or if Bidi processing is missing.
- [x] Task: Conductor - User Manual Verification 'Investigation & Reproduction' (Protocol in workflow.md) [checkpoint: b370060]

## Phase 2: Core Logic Fix
- [x] Task: Update `factories/mushaf_fast_render.py`. [checkpoint: 4e1df60]
    - [x] Remove any erroneous manual reversals of the `words` list.
    - [x] Integrate `bidi.algorithm.get_display` to process the joined word string.
    - [x] Ensure that for Ayah lines, words are joined in logical order (`1, 2, 3...`) and then Bidi-reordered.
- [x] Task: Update `factories/single_clip.py` if the shared `pre_render_static_page` logic contains the same bug. [checkpoint: 4e1df60]
- [x] Task: Verify the fix using the reproduction script. [checkpoint: 4e1df60]
- [x] Task: Conductor - User Manual Verification 'Core Logic Fix' (Protocol in workflow.md) [checkpoint: 4e1df60]

## Phase 3: Engine Verification & Cleanup
- [ ] Task: Generate a full 5-second snippet using the FFmpeg engine and verify RTL flow visually.
- [ ] Task: Synchronize `conductor/product.md` if any technical details of the RTL implementation have shifted.
- [ ] Task: Conductor - User Manual Verification 'Engine Verification & Cleanup' (Protocol in workflow.md)
