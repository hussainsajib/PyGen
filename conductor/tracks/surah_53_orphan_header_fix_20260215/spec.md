# Specification: Fix Orphan Header/Basmalah Page for Surah 53

## Overview
Fix a bug in the Mushaf video generation process where Surah 53 generates an "orphan" initial page containing only the Surah Header and Basmalah. The desired behavior is for the Header and Basmalah to be merged with the first Ayah on the first page/frame of the video, skipping the isolated page.

## Context
User reports that previous attempts to fix this issue have failed. The current output for Surah 53 separates the header information from the content, likely due to pagination logic that pushes the header to a new page when the previous Surah ends near the bottom of a page, but fails to pull the first Ayah up or push the header down correctly to join them.

## Reproduction
- **Command:** `python processes/mushaf_video.py 53`
- **Observation:** Check the first few seconds/frames of the generated video or the debug output frames. Currently, it shows a page with only Header + Basmalah.

## Requirements

### Functional Requirements
1.  **Orphan Page Detection/Prevention:** The system must identify when a page layout results in *only* a Surah Header and/or Basmalah without any Ayah text.
2.  **Content Merging:** Modify the page generation or video frame composition logic to ensure that for Surah 53 (and similar cases), the Surah Header and Basmalah are displayed on the same page/frame as the first Ayah of the Surah.
3.  **Frame Skipping:** Ensure the "orphan" page (containing only non-Ayah assets) is not generated as a video frame.

### Verification Scope
1.  **Primary Target:** Verify the fix specifically on Surah 53.
2.  **Regression/Pattern Testing:** Identify other Surahs that share this layout characteristic (starting on a new page after a full previous page) and verify the fix applies correctly to them without breaking normal layouts.

## Success Criteria
- The first frame of the generated video for Surah 53 displays the Surah Header, Basmalah, and the first Ayah together.
- The video flows immediately into the recitation of the first Ayah without a silent or static "header-only" segment.
