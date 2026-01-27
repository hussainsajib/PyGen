# Plan: Refactor Mushaf Rendering Verification Script

This plan outlines the refactoring of `scripts/verify_mushaf_rendering.py` to integrate latest fonts, RTL logic, and robust database sourcing.

## Phase 1: Data Access & Structure Integration
- [x] Task: Update database connection and retrieval logic. 9d88086
    - [x] Write unit tests for `get_page_data` (mocking SQLite).
    - [x] Implement robust retrieval of lines including `line_type`, `surah_number`, and `words` from `qpc-v2-15-lines.db` and `word_by_word_qpc-v2.db`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Data Access' (Protocol in workflow.md) 9d88086

## Phase 2: Core Rendering Logic Refactor
- [x] Task: Implement dynamic font selection and loading. 6334762
    - [x] Write unit tests for font path resolution.
    - [x] Implement logic to select fonts based on `line_type` (BSML, SURA, page font).
- [x] Task: Implement RTL word sequencing. 6334762
    - [x] Write unit tests for RTL string construction.
    - [x] Refactor word joining to reverse word order before rendering.
- [x] Task: Integrate Pillow-based text rendering. 6334762
    - [x] Implement/Update `render_mushaf_text_to_image` within the script.
    - [x] Add fallback mechanism for decorative fonts.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Core Rendering' (Protocol in workflow.md) 6334762

## Phase 3: Integration and Bug Fixes
- [x] Task: Refactor the main verification loop. 221d42c
    - [x] Update the script to loop through selected pages and generate verification images.
    - [x] Fix any existing bugs in coordinate calculation or output directory handling.
- [x] Task: Perform final end-to-end verification. 221d42c
    - [x] Generate verification frames for Page 1 (Surah 1) and Page 2 (Surah 2).
    - [x] Confirm visual alignment with the main video generation engine.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Final Verification' (Protocol in workflow.md) 221d42c
