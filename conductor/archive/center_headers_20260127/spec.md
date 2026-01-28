# Specification: Vertically Center Bismillah and Surah Header

## 1. Overview
**Type:** Bug Fix / Visual Refinement
**Goal:** Correct the vertical alignment of the Bismillah and Surah Header texts in the Mushaf video generation. Currently, these texts are rendered too high within their decorative containers. The objective is to perfectly center them vertically.

## 2. Functional Requirements
- **Bismillah Alignment:** The text rendered using `QCF_BSML.TTF` must be vertically centered within its designated decorative area/border.
- **Surah Header Alignment:** The Surah name text (rendered using `QCF_SurahHeader_COLOR-Regular.ttf`) must be vertically centered within the Surah header decorative strip.
- **Consistency:** The centering must be consistent across all Surahs and page layouts in the Mushaf video generator.

## 3. Implementation Details
- **Scope:** This change is specific to the `mushaf_video` generation process (likely within `processes/mushaf_video.py` or `factories/image.py` where text drawing occurs).
- **Metric:** "Centered" is defined as having equal visual padding above and below the text glyphs relative to the container borders.

## 4. Acceptance Criteria
- [ ] Bismillah text appears visually centered (not sitting high) in generated frames.
- [ ] Surah Header text appears visually centered in generated frames.
- [ ] No regression in horizontal alignment or font size.
