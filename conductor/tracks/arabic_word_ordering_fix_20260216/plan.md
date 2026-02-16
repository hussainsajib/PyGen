# Implementation Plan - Fix Arabic Word Ordering in Fast Engines

## Phase 1: Investigation & Reproduction
- [x] Task: Create a reproduction script `reproduce_alignment_bug.py` using `MushafRenderer` to save a frame containing a multi-word line (e.g., Page 2. [checkpoint: 8629644]
    - [x] Verify that words are currently arranged LTR.
- [x] Task: Analyze `factories/mushaf_fast_render.py` (`_prepare_renderable_lines` and `prepare_static_base`). [checkpoint: 8629644]
- [x] Task: Conductor - User Manual Verification 'Investigation & Reproduction' (Protocol in workflow.md) [checkpoint: 8629644]

## Phase 2: Core Logic Fix
- [x] Task: Write failing unit tests in `tests/test_arabic_word_ordering.py`. [checkpoint: a6e1d54]
    - [x] Mock word data and verify string concatenation order.
- [x] Task: Update `factories/mushaf_fast_render.py` to reverse word lists before joining. [checkpoint: a6e1d54]
- [x] Task: Update `factories/single_clip.py` (if applicable) to ensure parity. [checkpoint: a6e1d54]
- [x] Task: Verify the fix with `reproduce_alignment_bug.py`. [checkpoint: a6e1d54]
- [x] Task: Conductor - User Manual Verification 'Core Logic Fix' (Protocol in workflow.md) [checkpoint: a6e1d54]

## Phase 3: Engine Verification & Cleanup
- [x] Task: Generate a full video snippet for a Juz using the FFmpeg engine and visually inspect for RTL alignment. [checkpoint: 4b35779]
- [x] Task: Synchronize `conductor/product.md` documentation. [checkpoint: 4b35779]
- [x] Task: Conductor - User Manual Verification 'Engine Verification & Cleanup' (Protocol in workflow.md) [checkpoint: 4b35779]
