# Specification: Mushaf Video Multi-Page Recitation Fix

## Overview
Fix a bug in the Mushaf video generator where recitation continues across multiple pages but only the first page's text is displayed. Ensure that the video correctly transitions to the next Mushaf page when the recitation moves beyond the current page's lines.

## Functional Requirements
- **Page-Aware Chunking:**
    - The chunking logic must be modified to ensure that every chunk belongs to exactly one Mushaf page.
    - A new chunk must be started immediately whenever a line from a different page is encountered in the sequence.
- **Persistent Multi-Page Rendering:**
    - The video composition must include clips for every page spanned by the Surah's recitation.
    - Each page transition must result in a clean clip swap in the final video.
- **Conditional Header Injection:**
    - Surah headers and Basmallah lines must ONLY be injected into the first chunk of the FIRST page of a Surah.
    - All subsequent chunks and pages within the same Surah must only display standard Ayah lines.

## Non-Functional Requirements
- **Fluid Transitions:** Page transitions should happen exactly at the start of the first Ayah on the new page.
- **Scalability:** The logic must support any number of pages (e.g., long Surahs like Al-Baqarah).

## Acceptance Criteria
1. Generating a video for Surah 87 (spans Page 591 and 592) shows 4 lines on the first clip, then swaps to the full set of lines for the second page.
2. The Surah header and Basmallah are only visible on the first page.
3. The second page correctly loads its specific font (`p592.ttf`) and text content.
4. No gaps in audio or visual continuity during page turns.

## Out of Scope
- Animating the "page turn" effect (direct cut is sufficient).
- Changing the layout logic for non-Mushaf videos.
