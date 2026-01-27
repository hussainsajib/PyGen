# Specification: Mushaf Video Dynamic Highlighting Width

## Overview
Improve the visual quality of Mushaf videos by adjusting the highlighting logic to only cover the actual text portion of each line, rather than the entire frame width.

## Functional Requirements
- **Dynamic Width Calculation:**
    - For each line of type `ayah`, calculate the width of the highlighted block based on the visual width of the rendered text image (post-trimming).
    - Add a small horizontal padding (e.g., 20px total) to the calculated width to ensure the highlight slightly exceeds the text boundaries for better aesthetics.
- **Horizontal Centering:**
    - Position the dynamic highlight block such that its horizontal center aligns with the horizontal center of the frame (matching the text's horizontal position).
- **Consistency:**
    - Maintain the existing vertical positioning logic where the highlight is centered on the line slot.
    - Maintain the existing timing logic where the highlight is only visible during the line's recitation.

## Non-Functional Requirements
- **Visual Accuracy:** The highlight must precisely follow the boundaries of the text on every line, regardless of line length.
- **Stability:** Ensure no flickering or misalignment between the text image and the highlight block.

## Acceptance Criteria
1. Generated Mushaf videos show highlight blocks that match the width of the Arabic text on each line.
2. Short lines (like the end of a Surah) have short highlights.
3. Long lines (justified text) have wide highlights.
4. No highlight is shown for Surah headers or Basmallah (as per existing rules).

## Out of Scope
- Implementing word-level highlighting (highlighting currently operates at the line level).
- Changing the highlight color or opacity.
