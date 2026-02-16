# Specification: Revert Metadata Layout to Footer with Background Bar

## Overview
Revert the Mushaf and Juz video layouts from the current sidebar-based metadata stack back to a traditional horizontal footer. The footer will be enhanced with a semi-transparent background bar to improve text legibility and will be positioned slightly above the bottom edge of the screen.

## Layout Requirements

### 1. Footer Bar
-   **Structure:** A horizontal semi-transparent background bar spanning the width of the screen (or the usable content area).
-   **Position:** Floating slightly above the bottom edge of the screen.
-   **Content Alignment:**
    -   **Reciter Name:** Left-aligned within the footer bar.
    -   **Surah/Juz Name:** Center-aligned within the footer bar.
    -   **Brand Name:** Right-aligned within the footer bar.
-   **Margins:** Maintain consistent horizontal padding/margins from the screen edges for the left and right elements.

### 2. Styling
-   **Background:** Semi-transparent (e.g., black or a dark color with ~40-60% opacity) to ensure text pops regardless of the underlying video/image background.
-   **Text:** Maintain existing font (`kalpurush.ttf`) and color consistency.

### 3. Scope
-   Applies to **standalone Mushaf videos** and **Juz Mushaf videos**.
-   Applies to **Horizontal (16:9)** and **Vertical (9:16/Shorts)** formats.
-   Requires updates to both the **standard MoviePy engine** and the **high-speed rendering engines** (Fast Engine).

## Functional Requirements
-   Remove the recently added left sidebar metadata stacking logic.
-   Re-implement horizontal footer positioning logic in `processes/video_configs.py`.
-   Update `factories/mushaf_fast_render.py` and `factories/single_clip.py` to render the new background bar and correctly position the text elements.

## Acceptance Criteria
- [ ] Footer metadata (Reciter, Surah, Brand) is arranged horizontally.
- [ ] A semi-transparent background bar is visible behind the footer text.
- [ ] The footer is positioned slightly above the bottom edge.
- [ ] The layout is consistent across all video types and engines.
- [ ] The previous sidebar metadata layout is completely removed.
