# Implementation Plan: Authentic Mushaf Rendering Update

This plan details the steps to enhance the `/mushaf` feature with authentic rendering using the structural layout database and specialized fonts, ensuring zero impact on other application features.

## Phase 1: Backend Infrastructure (FastAPI)
- [x] Task: Research existing Mushaf data retrieval logic in `db_ops/crud_mushaf.py` and `app.py`.
- [x] Task: Create backend unit tests for the enhanced Mushaf page data retrieval.
    - [x] Write tests to verify correct joining of words based on `first_word_id` and `last_word_id`.
    - [x] Write tests to verify `line_type` and `is_centered` are correctly returned for all 15 lines.
- [x] Task: Implement the structured page retrieval logic in `db_ops/crud_mushaf.py`.
    - [x] Update `get_mushaf_page_data` (or create a specific version for the viewer) to fetch all fields from the `pages` table.
    - [x] Implement word concatenation logic for `ayah` lines.
- [x] Task: Ensure the Mushaf API endpoint in `app.py` returns the new structured data format.
- [x] Task: Conductor - User Manual Verification 'Backend Infrastructure' (Protocol in workflow.md)

## Phase 2: Frontend Implementation (Jinja2/HTML/CSS)
- [x] Task: Analyze the current `templates/mushaf.html` and its styling.
- [x] Task: Update `templates/mushaf.html` to handle the structured line data.
    - [x] Implement conditional rendering logic for `surah_name`, `basmallah`, and `ayah`.
    - [x] Implement the overlaid Surah name typography (Text on design header).
- [x] Task: Update CSS in `templates/mushaf.html` to support the new font mappings.
    - [x] Define `@font-face` rules for `QCF_BSML.TTF`, `QCF_SURA.TTF`, and `QCF_SurahHeader_COLOR-Regular.ttf`.
    - [x] Implement the `is_centered` (centered vs. justified) alignment logic.
- [x] Task: Conductor - User Manual Verification 'Frontend Implementation' (Protocol in workflow.md)

## Phase 3: Integration and Verification
- [x] Task: Verify that the Mushaf Viewer displays page 1 (Fatiha) and page 2 (Baqarah) with perfect alignment and authentic fonts.
- [x] Task: Perform a regression check on the Word-by-Word (WBW) and Video Generation features to ensure zero side effects.
- [x] Task: Conductor - User Manual Verification 'Integration and Verification' (Protocol in workflow.md)
