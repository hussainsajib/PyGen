# Implementation Plan: Mushaf Video Header Boundary Refinement

## Phase 1: Core Logic Refinement (TDD)
Refine the scene grouping utility to precisely handle orphaned headers based on Ayah content presence.

- [x] Task: Create new failing test cases in `tests/test_mushaf_boundary_logic.py`. 05a9995
    - [x] Case 1: Surah starting with ONLY Header/Basmallah on first page (must defer).
    - [x] Case 2: Surah starting with Header + at least 1 Ayah on first page (must NOT defer).
- [x] Task: Update `group_mushaf_lines_into_scenes` in `db_ops/crud_mushaf.py` to support the new "defer only if zero Ayahs" logic. 05a9995
    - [x] Add a `defer_if_no_ayah: bool = False` parameter.
    - [x] Implement check: `has_ayah = any(l.get('line_type') == 'ayah' for l in page_lines)`.
- [x] Task: Conductor - User Manual Verification 'Core Logic Refinement (TDD)' (Protocol in workflow.md) 05a9995

## Phase 2: Process Integration
Enable the refinement for standalone Mushaf videos while ensuring Juz videos remain authentic to the Mushaf layout.

- [x] Task: Update `processes/mushaf_video.py` (`generate_mushaf_video`) to pass `defer_if_no_ayah=True` to the grouping utility. 3f91051
- [x] Task: Update `processes/mushaf_fast_video.py` (`generate_mushaf_fast`) to pass `defer_if_no_ayah=True` for standalone videos. 3f91051
- [x] Task: Explicitly ensure `generate_juz_video` passes `defer_if_no_ayah=False` (preserving current behavior). 3f91051
- [x] Task: Conductor - User Manual Verification 'Process Integration' (Protocol in workflow.md) 3f91051

## Phase 3: Visual Verification & Documentation
Verify the fix with real Surah data and update project documentation.

- [x] Task: Create `scripts/verify_boundary_refinement.py` to generate a standalone video for Surah 53 and verify the header is moved to Page 526 content. 3f91051
- [x] Task: Verify Surah 108 (starts mid-page with Ayahs) still renders its header on the first scene. 3f91051
- [x] Task: Synchronize `conductor/product.md` to reflect the refined "Intelligent Scene Grouping" behavior. 3f91051
- [x] Task: Conductor - User Manual Verification 'Visual Verification & Documentation' (Protocol in workflow.md) 3f91051
