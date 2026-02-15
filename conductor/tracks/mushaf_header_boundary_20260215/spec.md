# Specification: Mushaf Video Header Boundary Refinement

## Overview
This track addresses a visual layout issue in standalone Mushaf videos where Surah Headers (`surah_name`) or `basmallah` lines are "orphaned" at the end of a Mushaf page. To improve the visual flow, these starting headers will be shifted to the top of the subsequent page's scene if they appear on a page with no actual Ayah text from that Surah.

## Functional Requirements
1.  **Generalized Header Shifting Logic:**
    -   Apply to **any Surah** where the starting Mushaf page contribution consists **ONLY** of non-Ayah lines (e.g., `surah_name`, `basmallah`, or both).
    -   If the starting page contains **zero** lines of actual `ayah` text for the target Surah, those starting non-Ayah lines must be deferred.
    -   Deferred lines must be prepended to the beginning of the lines retrieved from the next Mushaf page to form the first "scene" of the video.
2.  **Orphaned Page Exclusion:**
    -   When shifting occurs, the original page that contained only the orphaned headers must be completely skipped during the video assembly.
3.  **Strict Ayah Threshold:**
    -   If the preceding page contains at least **one line of actual Ayah text** from that Surah, the header shifting logic must **not** apply. The page must be rendered exactly as it appears in the Mushaf.
4.  **Process Selectivity:**
    -   This shifting behavior must apply **ONLY** to standalone Mushaf videos (both standard and high-speed).
    -   **Juz Mushaf** videos are explicitly excluded; they must maintain original Mushaf page boundaries to preserve physical layout continuity across the full volume.
5.  **Cross-Engine Implementation:**
    -   The logic must be implemented within the shared data preparation layer to ensure consistency between the standard MoviePy engine and the high-speed engines (FFmpeg, OpenCV, etc.).

## Non-Functional Requirements
-   **Data Consistency:** Ensure that prepended lines maintain their original properties (e.g., `page_number`, `line_number`) while being rendered in the new scene.

## Acceptance Criteria
- [ ] Any Surah starting with orphaned headers (no Ayah on the first page) has its first video scene starting with those headers followed by the next page's content.
- [ ] Standalone video for Surah 53 starts with its header and Basmallah prepended to Page 526 content; Page 525 is not rendered.
- [ ] Standalone video for a Surah starting mid-page with at least one Ayah (e.g., Surah 2) renders normally.
- [ ] Juz 30 video maintains original boundaries for all Surah transitions.

## Out of Scope
-   Modifying the `group_mushaf_lines_into_scenes` logic for Juz videos.
