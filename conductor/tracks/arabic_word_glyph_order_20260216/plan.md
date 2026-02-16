# Implementation Plan - Arabic Word and Glyph Ordering Fix

## Phase 1: Investigation and Reproduction
- [ ] Task: Create a reproduction script `reproduce_alignment_bug.py` that uses the `MushafRenderer` (Fast engine logic) to render Surah 2, Ayah 5 and save a frame.
- [ ] Task: Analyze the existing word joining logic in `factories/mushaf_fast_render.py` (`_prepare_renderable_lines` and `prepare_static_base`).
    - [ ] Determine if words are being reversed manually or if Pillow is expected to handle RTL.
- [ ] Task: Conductor - User Manual Verification 'Investigation and Reproduction' (Protocol in workflow.md)

## Phase 2: Core Logic Fix (Fast Engine)
- [ ] Task: Write failing unit tests in `tests/test_arabic_alignment.py`.
    - [ ] Test string assembly for Surah 2, Ayah 5, Word 5.
- [ ] Task: Update `factories/mushaf_fast_render.py` to use `arabic_reshaper` and `bidi.algorithm` (if necessary) or fix the manual reversal logic.
    - [ ] Ensure that for a single line, words are ordered RTL, AND the internal glyphs of each word are also correctly ordered.
- [ ] Task: Update `factories/single_clip.py` if shared static page rendering logic needs similar fixes.
- [ ] Task: Verify the fix with `reproduce_alignment_bug.py`.
- [ ] Task: Conductor - User Manual Verification 'Core Logic Fix (Fast Engine)' (Protocol in workflow.md)

## Phase 3: Final Verification and Documentation
- [ ] Task: Generate a full short video for Surah 2 using the FFmpeg engine and visually inspect for alignment issues.
- [ ] Task: Synchronize `conductor/product.md` if any technical requirements for RTL rendering have changed.
- [ ] Task: Conductor - User Manual Verification 'Final Verification and Documentation' (Protocol in workflow.md)
