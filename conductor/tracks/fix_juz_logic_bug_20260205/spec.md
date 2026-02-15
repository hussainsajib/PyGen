# Specification: Fix Juz Mushaf Video Generation Logic

## Overview
A critical bug has been identified in the recently implemented Juz-based Mushaf video generation feature. Users report that generated videos only contain the initial Bismillah (approximately 5 seconds) instead of the full Juz content. The system incorrectly marks these jobs as "Done" despite the missing content.

## Goals
- Identify and resolve the logic error preventing full Juz video assembly.
- Ensure that audio concatenation and timestamp mapping correctly span all Surahs within a Juz.
- Verify that paging and line assembly logic correctly includes all relevant Ayah lines for the selected Juz.

## Functional Requirements
- **Audio & Timing Fix:**
    - Debug `calculate_juz_offsets` and `concatenate_audioclips` integration to ensure the final audio stream covers the entire Juz.
    - Validate that `all_wbw_timestamps` composite keys (`surah:ayah`) are correctly utilized by the rendering engine.
- **Paging & Rendering Fix:**
    - Audit the `sorted_pages` calculation and `lines_by_page` filtering logic in `generate_juz_video`.
    - Ensure that headers, Basmallah, and Ayah lines are correctly sequenced across multiple Surahs and pages.
- **Job Status Integrity:**
    - Ensure that any generation failure results in a "Failed" status in the job queue rather than a misleading "Done" status with an empty video.

## Non-Functional Requirements
- **Robustness:** Implement logging to track the number of Surahs and pages processed during Juz generation.
- **Parity:** Maintain all visual enhancements (borders, progress bars) for the full Juz duration.

## Acceptance Criteria
- [ ] A Juz video (e.g., Juz 1 or Juz 30) is generated with its full intended duration (multiple minutes/hours).
- [ ] The video contains all Ayahs from the start Surah/Ayah to the end Surah/Ayah of the selected Juz.
- [ ] Word-level highlighting is synchronized correctly throughout the entire video, including transitions between Surahs.
- [ ] The progress bar correctly reflects the percentage of the entire Juz completed.

## Out of Scope
- Adding new UI features to the Juz interface.
- Modifying standard Surah-based Mushaf generation (unless fixing shared logic).
