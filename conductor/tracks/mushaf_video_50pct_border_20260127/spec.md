# Specification: Mushaf Video 50% Border Width

## Overview
Adjust the visual structure of Mushaf videos to use a significantly narrower border width (50% of the total frame width) to create a more focused, book-like appearance.

## Functional Requirements
- **Reduced Border Width:**
    - Update the `border_w` calculation in the video generation engine to use `width * 0.50` instead of the current `width * 0.90`.
    - This applies to both horizontal and vertical video formats.
- **Content Alignment:**
    - Ensure the Mushaf text area, Surah headers, and Basmallah remain horizontally centered within this narrower border.
    - Maintain the existing dynamic highlighting logic, which will now naturally be constrained by the narrower text boundaries.
- **Visual Styling:**
    - Retain the authentic double-gold border and paper texture implementation.
    - Retain the current font sizes and vertical line spacing.

## Non-Functional Requirements
- **Consistency:** The 50% width must be static and uniform across all pages of the generated video.
- **Visual Stability:** No clipping or misalignment should occur due to the narrower container.

## Acceptance Criteria
1. Generated Mushaf videos show a border that is exactly half the width of the video frame.
2. All Quranic text, headers, and highlighting are contained within and centered in this 50% area.
3. Overlays (Reciter, Surah, Brand) remain in their standard positions at the bottom of the full frame.
4. No regressions in texture rendering or border aesthetics.

## Out of Scope
- Dynamically changing the width per-page.
- Changing the vertical margins or font sizes.
