# Specification: Authentic Mushaf Video Border

## Overview
Transform the Mushaf video border from a simple outline into an authentic "book-like" frame. This involves using a double-bordered structure, a fixed width for global consistency, and subtle texturing to simulate physical paper.

## Functional Requirements
- **Fixed-Width Frame:** 
    - The border will use a fixed width (e.g., 90% of the video width) across all pages to ensure visual stability.
- **Double Border Design:**
    - Render a "double" border (an outer thick line and a thinner inner line) to give the frame a traditional "book cover" weight.
    - **Color:** Gold/Bronze (`#D4C5A1`).
- **Paper Texture Simulation:**
    - Apply a subtle grain or paper-like texture to the area inside the border.
    - Maintain the existing background color (or use a dedicated cream color) as the base for this texture.
- **Layout Persistence:**
    - The border and its inner textured area remain static throughout the entire video.
    - Overlays (Reciter, Surah, Brand) will remain in their current positions at the bottom of the full frame, outside/separate from the Mushaf "page" area.

## Non-Functional Requirements
- **Visual Parity:** The "page" area should closely resemble the aesthetic of the `/mushaf` web viewer.
- **Rendering Performance:** The texture should be implemented as a static image or a lightweight filter to avoid significant increases in video encoding time.

## Acceptance Criteria
1. Generated Mushaf videos show a thick double-gold border with a fixed width.
2. The area inside the border has a subtle paper texture.
3. The border does not change size or flicker during page transitions.
4. Standard overlays remain legible at the bottom of the screen.

## Out of Scope
- Implementing a "flipping" page transition effect.
- Dynamic resizing of the border based on text length.
