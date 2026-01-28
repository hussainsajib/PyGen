# Specification: Mushaf Video Vertical Centering and Spacing

## 1. Overview
**Type:** Feature / Visual Refinement
**Goal:** Adjust the vertical layout of the Mushaf video generation to center the main content block vertically within the screen and increase the spacing between the Surah Header and the Bismillah.

## 2. Functional Requirements
- **Vertical Centering:**
    - The entire block of content (Surah Header + Bismillah + Ayah Lines) must be vertically centered within the video frame.
    - This centering logic should apply to both full pages and partial pages (e.g., end of Surah).
    - The structural integrity of the 15-line grid should be maintained where applicable, but the visual block itself moves to the center.
- **Header Spacing:**
    - Increase the vertical gap between the Surah Header and the Bismillah text.
    - **Specific Value:** Increase by approximately 20px (or a proportionate value relative to resolution).

## 3. Implementation Details
- **Rendering Logic:**
    - Modify `factories/single_clip.py` (specifically `generate_mushaf_page_clip`).
    - Calculate the total height of the content block.
    - Calculate the new starting Y-coordinate to achieve vertical centering: `start_y = (screen_height - content_height) / 2`.
    - Adjust the Y-coordinate calculation for the Bismillah line specifically to add the extra padding/gap.

## 4. Acceptance Criteria
- [ ] The entire text block is visually centered vertically in the final video.
- [ ] The gap between the Surah Header and Bismillah is noticeably larger (approx. +20px).
- [ ] The relative structure of the lines remains consistent (no overlapping or broken grid).
- [ ] Works correctly for both short (vertical) and long (horizontal) video formats.
