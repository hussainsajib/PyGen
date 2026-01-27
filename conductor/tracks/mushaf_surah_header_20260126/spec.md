# Specification: Mushaf Surah Header Integration

## Overview
Enhance the Mushaf video generator to include authentic Surah headers at the beginning of each Surah, utilizing specialized fonts to match traditional Mushaf aesthetics.

## Functional Requirements
- **Surah Header Rendering:** Implement rendering of the Surah header at the top of the scene when a video starts at the beginning of a Surah (Ayah 1).
- **Positioning:** The header must be centered at the very top of the frame, positioned above the first line of Quranic text.
- **Typography:**
    - Use the `QCF_SurahHeader_COLOR-Regular.ttf` font for the header.
    - Scale the header font size to visually match the size of the main Quranic text on the page.
- **Trigger Logic:** The header should only be displayed if the video segment includes the first Ayah of a Surah.

## Non-Functional Requirements
- **Visual Consistency:** The header should maintain the same margins and alignment principles as the rest of the Mushaf layout.
- **Performance:** Rendering the header should not significantly increase video generation time.

## Acceptance Criteria
1. When generating a Mushaf video starting from Ayah 1 of any Surah, a centered Surah header is visible at the top.
2. The Surah header uses the correct `QCF_SurahHeader_COLOR-Regular.ttf` font.
3. The size of the Surah header is visually consistent with the main Quranic text.
4. The Surah header does not appear on subsequent "pages" or scenes within the same Surah if they do not start with Ayah 1.

## Out of Scope
- Integration of Surah headers into the non-Mushaf (Word-by-Word Interlinear) generator.
- Customizing the Surah header text beyond what is provided by the specialized font.
