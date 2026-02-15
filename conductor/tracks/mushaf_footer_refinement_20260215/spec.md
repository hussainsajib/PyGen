# Specification: Mushaf Video Footer Refinement

## Overview
This track addresses a visual bug where footer information (Reciter Name, Surah Name, Brand Name) in Mushaf videos is rendered as "boxes" instead of the intended Bengali text. This issue occurs across both standard MoviePy and high-speed engines due to font loading failures in PIL and potentially MoviePy.

## Functional Requirements
1.  **Correct Font Loading:**
    -   Identify and implement a robust mechanism to load the "Kalpurush" font across all rendering backends.
    -   Ensure the high-speed engine (`factories/mushaf_fast_render.py`) uses the absolute system path or a local copy of `kalpurush.ttf`.
    -   Update `factories/single_clip.py` to correctly resolve font paths for PIL-based rendering.
2.  **Visual Styling Consistency:**
    -   Ensure footer text is rendered sharply and matches the `FONT_COLOR` configuration.
    -   Maintain current positioning and sizing as defined in `processes/video_configs.py`.
3.  **Cross-Engine Support:**
    -   The fix must apply to both the stable MoviePy engine and the experimental high-speed engines.

## Non-Functional Requirements
-   **Reliability:** The system should gracefully handle missing fonts by falling back to a supported system font while logging a warning.
-   **Maintainability:** Centralize font path resolution to avoid duplication.

## Acceptance Criteria
- [ ] Footer text (Reciter, Surah, Brand) is correctly rendered in Bengali without "boxes" in both standard and high-speed videos.
- [ ] Visual styling (color, size) is consistent across all engines.
- [ ] High-speed engine successfully loads `kalpurush.ttf` from the identified system path or a defined local path.

## Out of Scope
-   Changing the footer content or logic.
-   Changing the default font from Kalpurush.
