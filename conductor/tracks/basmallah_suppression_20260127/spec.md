# Specification: Basmallah Suppression for Surah 1 and Surah 9

## Overview
Ensure that the Basmallah is not duplicated for Surah 1 (where it is part of the first Ayah) and is never displayed for Surah 9 (where it does not exist). This applies to both the `/mushaf` web viewer and the generated Mushaf videos.

## Functional Requirements
- **Global Suppression (Surah 1 & 9):** Automatically suppress lines of type `basmallah` when they belong to Surah 1 or Surah 9.
- **Backend Enforcement:**
    - Modify `db_ops/crud_mushaf.py` functions (`get_mushaf_page_data`, `get_mushaf_page_data_structured`) to filter out `basmallah` lines for these specific Surahs.
- **Video Generator Synchronization:**
    - Ensure `processes/mushaf_video.py` correctly skips Basmallah injection for Surah 1 and Surah 9.
    - Verify that Surah 1's Ayah 1 (which contains the Basmallah text in the font) renders correctly without a separate header line.

## Non-Functional Requirements
- **Data Integrity:** The underlying database remain unchanged; suppression happens during data retrieval/processing.
- **Consistency:** Visual parity between the web viewer and generated videos.

## Acceptance Criteria
1. Opening Page 1 (Surah 1) in the web viewer shows only the Surah header and Ayah 1 (no separate Basmallah line).
2. Generating a video for Surah 1 shows only the Surah header and Ayah 1.
3. Opening/Generating Surah 9 shows only the Surah header (no Basmallah).
4. All other Surahs (2-8, 10-114) correctly show the Basmallah header.

## Out of Scope
- Modifying the font glyphs themselves.
- Changing the layout for non-Mushaf (Word-by-Word Interlinear) videos.
