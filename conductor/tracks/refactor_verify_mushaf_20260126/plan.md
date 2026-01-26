# Plan: Refactor Mushaf Rendering Verification Script

This plan outlines the refactoring of `scripts/verify_mushaf_rendering.py` to integrate latest fonts, RTL logic, and robust database sourcing.

## Phase 1: Data Access & Structure Integration
- [x] Task: Update database connection and retrieval logic. 9d88086
    - [x] Write unit tests for `get_page_data` (mocking SQLite).
    - [x] Implement robust retrieval of lines including `line_type`, `surah_number`, and `words` from `qpc-v2-15-lines.db` and `word_by_word_qpc-v2.db`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Data Access' (Protocol in workflow.md) 9d88086

## Phase 2: Core Rendering Logic Refactor
- [ ] Task: Implement dynamic font selection and loading.
    - [ ] Write unit tests for font path resolution.
    - [ ] Implement logic to select fonts based on `line_type` (BSML, SURA, page font).
- [ ] Task: Implement RTL word sequencing.
    - [ ] Write unit tests for RTL string construction.
    - [ ] Refactor word joining to reverse word order before rendering.
- [ ] Task: Integrate Pillow-based text rendering.
    - [ ] Implement/Update `render_mushaf_text_to_image` within the script.
    - [ ] Add fallback mechanism for decorative fonts.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Core Rendering' (Protocol in workflow.md)

## Phase 3: Integration and Bug Fixes
- [ ] Task: Refactor the main verification loop.
    - [ ] Update the script to loop through selected pages and generate verification images.
    - [ ] Fix any existing bugs in coordinate calculation or output directory handling.
- [ ] Task: Perform final end-to-end verification.
    - [ ] Generate verification frames for Page 1 (Surah 1) and Page 2 (Surah 2).
    - [ ] Confirm visual alignment with the main video generation engine.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Verification' (Protocol in workflow.md)
