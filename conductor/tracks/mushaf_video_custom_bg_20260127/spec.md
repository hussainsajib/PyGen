# Specification: Mushaf Video Customizable Page Background & Media Selection

## Overview
Enable full media background support for Mushaf videos while providing granular control over the appearance of the "page" area inside the border, including custom color selection.

## Functional Requirements
- **Internal Page Background Configuration:**
    - **MUSHAF_PAGE_BACKGROUND_MODE:** Three available modes:
        - **Transparent:** No background color inside the border (shows full media).
        - **Semi-Transparent:** A translucent overlay inside the border.
        - **Solid:** A solid color fill inside the border.
    - **MUSHAF_PAGE_BACKGROUND_COLOR:** A customizable hex color (default: Cream `#FFFDF5`) applied in Solid and Semi-Transparent modes.
- **Rendering Logic Updates:**
    - Update `generate_mushaf_border_clip` in `factories/single_clip.py` to respect the selected mode and color.
    - Apply opacity based on mode: Solid (1.0), Semi-Transparent (0.5), Transparent (0.0).
    - Texture/noise is only applied in **Solid** mode.
- **Background Media Integration:**
    - Support applying an image or video background selected via the existing modal (Unsplash/Pexels).
- **Default Behavior:**
    - If no media is selected, default to a solid black background (`#000000`) for the full frame.
- **UI Integration:**
    - Add the background selection modal to the Mushaf creation page.
    - Add a **Mode Selector** (Transparent/Semi/Solid) and a **Color Picker** for the internal page color.

## Non-Functional Requirements
- **Visual Contrast:** The system should ensure that the combination of internal color and background media does not hinder text readability.
- **Maintainability:** Use shared components for background selection across video types.

## Acceptance Criteria
1. Mushaf videos correctly render the internal page area based on the chosen Mode and Color.
2. Users can pick a custom color (e.g., White, Light Green, Dark Blue) for the "page" via a color picker.
3. Media assets (Unsplash/Pexels) show clearly through the transparent and semi-transparent areas.
4. Background selection UI is synchronized between Mushaf and WBW.

## Out of Scope
- Configurable opacity levels (hardcoded to 0.5 for semi-transparent for now).
