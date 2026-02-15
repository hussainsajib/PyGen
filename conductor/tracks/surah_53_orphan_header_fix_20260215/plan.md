# Implementation Plan - Fix Orphan Header/Basmalah Page for Surah 53

## Phase 1: Investigation and Reproduction
- [ ] Task: Create a dedicated reproduction script `reproduce_orphan_header.py` that generates a video for Surah 53 using the standard `mushaf_video.py` logic but isolated for faster iteration.
- [ ] Task: Run the reproduction script to confirm the "orphan" header page issue (Header + Basmalah only on the first page).
- [ ] Task: Conductor - User Manual Verification 'Investigation and Reproduction' (Protocol in workflow.md)

## Phase 2: Implementation (Fixing the Pagination/Merging Logic)
- [ ] Task: Locate the page generation logic in `processes/mushaf_video.py` or the relevant layout engine (likely `factories/mushaf_fast_render.py` or similar) responsible for deciding page breaks.
- [ ] Task: Implement a check to detect if a page contains *only* non-content assets (Header, Basmalah) and lacks Ayah text.
- [ ] Task: Modify the logic to either:
    -   Pull the first Ayah of the Surah up to the current page if space permits (and if it was pushed only due to aggressive spacing).
    -   OR, more likely, push the Header and Basmalah down to the next page to join the first Ayah.
- [ ] Task: Verify the fix using the reproduction script `reproduce_orphan_header.py` ensuring the first frame now contains Header + Basmalah + Ayah.
- [ ] Task: Conductor - User Manual Verification 'Implementation (Fixing the Pagination/Merging Logic)' (Protocol in workflow.md)

## Phase 3: Verification and Regression Testing
- [ ] Task: Create a verification script `verify_orphan_fix.py` that checks the output of Surah 53 and a few other standard Surahs (e.g., 1, 112, 114) for layout correctness.
- [ ] Task: Run the verification script to ensure Surah 53 is fixed and no regressions were introduced in other Surahs.
- [ ] Task: Generate a full video for Surah 53 using `processes/mushaf_video.py` to confirm the final artifact is correct.
- [ ] Task: Conductor - User Manual Verification 'Verification and Regression Testing' (Protocol in workflow.md)
