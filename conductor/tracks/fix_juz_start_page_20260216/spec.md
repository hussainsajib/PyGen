# Specification: Fix Incorrect Start Page for Juz Video Basmallah

## Overview
Currently, when generating a Juz Mushaf video that starts in the middle of a Surah (e.g., Juz 2 starts at Al-Baqarah 142), the initial Basmallah injection erroneously displays the first page of that Surah (e.g., Page 2 for Al-Baqarah) instead of the actual starting page of the Juz (e.g., Page 22 for Juz 2). This track aims to ensure that the visual rendering during the initial Basmallah correctly reflects the Juz's start boundary.

## Requirements

### 1. Functional Requirements
- **Correct Start Page Mapping:** When a Juz video starts with a Basmallah injection, the renderer must use the Juz's metadata-defined start page for the first scene.
- **Mid-Surah Juz Support:** This fix must apply to all Juz that begin mid-Surah (Juz 2, 3, 4, etc.).
- **Visual Consistency:** The Mushaf page displayed during the injected Basmallah must match the page where the recitation actually begins.

### 2. Technical Requirements
- **Logic Update:** Modify the scene grouping and timestamp alignment logic in `processes/mushaf_video.py` (and high-speed variants if applicable) to prioritize the Juz start page for the initial injected segment.
- **Boundary Detection:** Ensure the `get_juz_boundaries` data is correctly used to initialize the `page_number` variable for the very first scene in the sequence.

## Success Criteria
- [ ] Juz 2 video displays Page 22 (the start of Juz 2) during the initial Basmallah.
- [ ] Subsequent Surah transitions within a Juz (e.g., the transition to Surah 3 in Juz 3) continue to play Basmallah and display the correct header page.
- [ ] Standalone Surah videos are unaffected and still show the Surah's first page for their Basmallah.
