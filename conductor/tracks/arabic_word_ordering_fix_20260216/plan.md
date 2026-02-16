# Implementation Plan - Fix Arabic Word Ordering in Fast Engines

## Phase 1: Investigation & Reproduction
- [ ] Task: Create a reproduction script `reproduce_alignment_bug.py` using `MushafRenderer` to save a frame containing a multi-word line (e.g., Page 2).
    - [ ] Verify that words are currently arranged LTR.
- [ ] Task: Analyze `factories/mushaf_fast_render.py` (`_prepare_renderable_lines` and `prepare_static_base`).
- [ ] Task: Conductor - User Manual Verification 'Investigation & Reproduction' (Protocol in workflow.md)

## Phase 2: Core Logic Fix
- [ ] Task: Write failing unit tests in `tests/test_arabic_word_ordering.py`.
    - [ ] Mock word data and verify string concatenation order.
- [ ] Task: Update `factories/mushaf_fast_render.py` to reverse word lists before joining.
- [ ] Task: Update `factories/single_clip.py` (if applicable) to ensure parity.
- [ ] Task: Verify the fix with `reproduce_alignment_bug.py`.
- [ ] Task: Conductor - User Manual Verification 'Core Logic Fix' (Protocol in workflow.md)

## Phase 3: Engine Verification & Cleanup
- [ ] Task: Generate a full video snippet for a Juz using the FFmpeg engine and visually inspect for RTL alignment.
- [ ] Task: Synchronize `conductor/product.md` documentation.
- [ ] Task: Conductor - User Manual Verification 'Engine Verification & Cleanup' (Protocol in workflow.md)
