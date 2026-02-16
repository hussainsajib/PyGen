# Implementation Plan - Arabic Word and Glyph Ordering Fix

## Phase 1: Investigation and Reproduction
- [x] Task: Create a reproduction script `reproduce_alignment_bug.py` that uses the `MushafRenderer` (Fast engine logic) to render Surah 2, Ayah 5 and save a frame. [checkpoint: 2cd6b21]
- [x] Task: Analyze the existing word joining logic in `factories/mushaf_fast_render.py` (`_prepare_renderable_lines` and `prepare_static_base`).
    - [x] Determine if words are being reversed manually or if Pillow is expected to handle RTL.
- [x] Task: Conductor - User Manual Verification 'Investigation and Reproduction' (Protocol in workflow.md) [checkpoint: 2cd6b21]

## Phase 2: Core Logic Fix (Fast Engine)
- [x] Task: Write failing unit tests in `tests/test_arabic_alignment.py`.
    - [x] Test string assembly for Surah 2, Ayah 5, Word 5.
- [x] Task: Update `factories/mushaf_fast_render.py` to use `arabic_reshaper` and `bidi.algorithm` (if necessary) or fix the manual reversal logic. [checkpoint: 2cd6b21]
    - [x] Ensure that for a single line, words are ordered RTL, AND the internal glyphs of each word are also correctly ordered.
- [x] Task: Update `factories/single_clip.py` if shared static page rendering logic needs similar fixes. [checkpoint: 2cd6b21]
- [x] Task: Verify the fix with `reproduce_alignment_bug.py`.
- [x] Task: Conductor - User Manual Verification 'Core Logic Fix (Fast Engine)' (Protocol in workflow.md) [checkpoint: 2cd6b21]

## Phase 3: Final Verification and Documentation
- [x] Task: Generate a full short video for Surah 2 using the FFmpeg engine and visually inspect for alignment issues. [checkpoint: 3045414]
- [x] Task: Synchronize `conductor/product.md` if any technical requirements for RTL rendering have changed.
- [x] Task: Conductor - User Manual Verification 'Final Verification and Documentation' (Protocol in workflow.md) [checkpoint: 3045414]
