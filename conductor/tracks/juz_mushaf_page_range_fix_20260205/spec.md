# Specification: Juz Mushaf Video Page Range & Audio Sync Fix

## 1. Overview
This track addresses a bug in the Juz Mushaf video generation where selecting a page range (e.g., 2 pages) within a Juz incorrectly results in a video containing the full Juz audio and duration. The fix ensures that both video and audio are strictly clipped to the requested page range, and that all necessary assets (Surahs, Mushaf pages, fonts) are identified and prepared before rendering begins.

## 2. Functional Requirements

### 2.1 Dynamic Surah & Page Mapping
- **Overlap Detection:** The system must query the `mushaf_pages` database at runtime to identify which Surahs and Ayahs overlap with the user-requested page range.
- **Audio Clipping:** Recitation audio must be strictly clipped to start at the beginning of the first requested page and end at the conclusion of the last requested page.
- **Duration Alignment:** The final video duration must exactly match the clipped audio duration.

### 2.2 Pre-flight Asset Validation
- **Dependency Mapping:** Before starting the rendering job, the system must generate a map of all required Surah audio files and QPC v2 fonts needed for the specific page range.
- **Asset Verification:** Scan for the existence of required `.ttf` fonts and database records.
- **Proactive Page Preparation:** Automatically trigger the generation or retrieval of any missing Mushaf page images before the video assembly phase begins.

### 2.3 Rendering Logic Updates
- **Juz Boundary Logic:** Update the Juz video generation engine to respect `start_page` and `end_page` parameters, overriding the default "full Juz" behavior.
- **Sync Accuracy:** Ensure word-level highlighting remains synchronized within the clipped audio/video window.

## 3. Acceptance Criteria
- [ ] A Juz video generated for a 2-page range has a duration corresponding only to those 2 pages.
- [ ] Audio starts precisely at the first word of the first page in the range.
- [ ] Audio ends precisely at the last word of the last page in the range.
- [ ] The system correctly identifies and prepares only the Surahs required for the selected pages.
- [ ] Missing Mushaf page images are automatically generated/verified before rendering.

## 4. Out of Scope
- Modifying the non-Mushaf (Word-by-Word Interlinear) video generator.
- Changes to the global configuration UI (unless required to pass page ranges).
