# Implementation Plan: Mushaf Video Footer Refinement

## Phase 1: Font Discovery & Centralization [checkpoint: bb41fc4]
Ensure all rendering backends can reliably locate and load the "Kalpurush" font.

- [x] Task: Create a utility `factories/font_utils.py` to resolve font paths, including system-level paths for common fonts like "Kalpurush". 3e12f81
- [x] Task: Write unit tests in `tests/test_font_utils.py` to verify that "Kalpurush" can be correctly resolved on the current OS. a627af7
- [x] Task: Refactor `factories/single_clip.py` and `factories/mushaf_fast_render.py` to use the new font utility. 35315f7
- [x] Task: Conductor - User Manual Verification 'Font Discovery & Centralization' (Protocol in workflow.md) bb41fc4

## Phase 2: Engine Integration & Fix [checkpoint: e204b02]
Apply the fixes to both the stable and experimental rendering engines.

- [x] Task: Create a visual specimen script `scripts/verify_footer_render.py` to generate frames with footers across all engines. e204b02
- [x] Task: Update `MushafRenderer` in `factories/mushaf_fast_render.py` to use the centralized font path for footer rendering. e204b02
- [x] Task: Update the standard renderer in `factories/single_clip.py` to ensure PIL-based text rendering uses the correct font path. e204b02
- [x] Task: Conductor - User Manual Verification 'Engine Integration & Fix' (Protocol in workflow.md) e204b02

## Phase 3: Final Verification & Documentation
Wrap up the track with final checks and documentation sync.

- [~] Task: Run a full generation for a short Surah (e.g., Surah 108) using both MoviePy and FFmpeg engines and visually verify the footers.
- [ ] Task: Update project documentation if any new font management guidelines were introduced.
- [ ] Task: Conductor - User Manual Verification 'Final Verification & Documentation' (Protocol in workflow.md)
