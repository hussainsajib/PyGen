# Specification: Mushaf Video Layout Redesign (Side Header & Stacked Footer)

## Overview
Redesign the Mushaf and Juz video layout to utilize the screen margins more effectively. The traditional footer information (Reciter, Surah, Brand) will be moved to a vertically centered stack on the left side. A new permanent Surah Header element will be added to the right side of the screen, vertically centered, using the same authentic glyphs as the in-page headers.

## Layout Changes

### 1. Left Sidebar (Metadata Stack)
-   **Content:** Reciter Name, Surah/Juz Name, Brand Name (in this order, top to bottom).
-   **Position:** Vertically centered on the screen.
-   **Alignment:** Horizontally left-aligned relative to the screen, but text within the stack is center-aligned.
-   **Margin:** "Some margin" from the left edge of the screen to ensure visibility and aesthetics.
-   **Styling:** Maintain existing footer font and color consistency.

### 2. Right Sidebar (Surah Header)
-   **Content:** The Surah Header glyph (same as used in the Mushaf page layout).
-   **Position:** Vertically centered on the screen.
-   **Alignment:** Horizontally right-aligned.
-   **Margin:** "Some margin" from the right edge of the screen.
-   **Visibility:** Appears on EVERY scene/page, positioned in the empty margin space to the right of the Ayah text block.

### 3. Footer Removal
-   The existing bottom footer bar will be removed as its content has moved to the left sidebar.

## Functional Requirements
-   **Consistent Rendering:** These changes must apply to both standard `Mushaf` videos and `Juz` videos.
-   **Engine Support:** Updates must be implemented in both the standard `MoviePy` engine and the `Fast` engines (FFmpeg/OpenCV).
-   **Glyph Reuse:** The right sidebar must reuse the authentic `QCF_SurahHeader` font glyphs dynamically based on the current Surah.

## Acceptance Criteria
- [ ] Left sidebar displays Reciter, Surah, and Brand stacked vertically and centered.
- [ ] Right sidebar displays the current Surah's header glyph vertically centered.
- [ ] The traditional bottom footer is gone.
- [ ] Layout looks balanced with appropriate margins on both sides.
