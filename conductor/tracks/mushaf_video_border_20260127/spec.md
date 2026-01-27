# Specification: Mushaf Video Area Border

## Overview
Enhance the Mushaf video aesthetic by adding a static, decorative border around the entire Mushaf text area, including Surah headers and Basmallah. This box will provide a clear structure and resemble the layout of a physical Mushaf.

## Functional Requirements
- **Static Border Rendering:**
    - Draw a visible border around the Mushaf content area.
    - **Scope:** The border must encompass all 15 line slots, including the space reserved for Surah headers and Basmallah.
    - **Persistence:** The border should be static and visible throughout the entire duration of every scene/clip.
- **Visual Styling:**
    - **Color:** Use a traditional color (e.g., Gold/Bronze or Dark Brown) to match the Islamic theme.
    - **Thickness:** Configurable or hardcoded to a visually distinct weight (e.g., 5-8 pixels).
    - **Padding:** Include internal padding (e.g., 20px) so the text does not touch the border.
    - **Corners:** Implement rounded corners for a modern, polished look.

## Non-Functional Requirements
- **Stability:** The border must remain perfectly static and not flicker during page turns or highlighting.
- **Layout Integrity:** The border must not overlap with existing overlays (Reciter name, Surah info, Brand).

## Acceptance Criteria
1. Generated Mushaf videos show a clearly defined box with rounded corners around the text area.
2. The box remains visible even when only a few lines of text are shown.
3. The box encompasses the header area at the top of the page.
4. No regressions in text alignment or highlighting logic.

## Out of Scope
- Adding intricate patterns or textures to the border (simple solid color is sufficient for now).
- Changing the background color of the Mushaf area (already covered by global background logic).
