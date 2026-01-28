# Specification: Mushaf Video Layered Background Refinement

## 1. Overview
**Type:** Feature / Refactor
**Goal:** Distinguish between the global video background and the inner page background (within the Mushaf border). This track introduces a layered background system where the page area can have its own mode (Transparent, Semi, Solid) while the outer area consistently follows the global `ACTIVE_BACKGROUND` or `BACKGROUND_RGB` configuration.

## 2. Functional Requirements
- **Global Background Logic (Outer Area):**
    - The primary video background must use `ACTIVE_BACKGROUND` (image or video URL) if provided.
    - If `ACTIVE_BACKGROUND` is empty, the background must fall back to `BACKGROUND_RGB`.
- **Page Background Logic (Inner Area):**
    - The background within the Mushaf border is governed by `MUSHAF_PAGE_BACKGROUND_MODE`:
        - **Transparent:** The inner area is fully transparent, revealing the global background directly.
        - **Semi:** The inner area has a color applied with a configurable opacity.
        - **Solid:** The inner area is fully opaque with the specified color.
    - **Opacity Configuration:** The "Semi" mode opacity must be user-configurable via a new setting `MUSHAF_PAGE_OPACITY`, represented as a value from 0 to 100.
- **Renaming & Configuration:**
    - Rename `MUSHAF_PAGE_BACKGROUND_COLOR` to `MUSHAF_PAGE_COLOR` globally across the codebase.
    - Update the frontend `/configs` page to include the slider for `MUSHAF_PAGE_OPACITY`.

## 3. Implementation Details
- **Configuration Update:** Global find-and-replace for `MUSHAF_PAGE_BACKGROUND_COLOR` to `MUSHAF_PAGE_COLOR`.
- **Frontend:** Update the Configs page to replace the old color field name and add a slider for `MUSHAF_PAGE_OPACITY`.
- **Rendering Logic:**
    - Modify `factories/single_clip.py` (specifically `generate_mushaf_page_clip` and `generate_mushaf_border_clip`) to implement the layered rendering.
    - The global background should be the bottom-most layer.
    - The Mushaf border and its internal fill (based on mode) should be layered above it.
    - In "Semi" mode, the alpha channel of the inner fill color should be calculated as `(MUSHAF_PAGE_OPACITY / 100) * 255`.

## 4. Acceptance Criteria
- [ ] Global video background correctly selects `ACTIVE_BACKGROUND` over `BACKGROUND_RGB`.
- [ ] `MUSHAF_PAGE_BACKGROUND_MODE` correctly applies to the inner border area only.
- [ ] "Transparent" mode shows the global background through the text area.
- [ ] "Semi" mode correctly applies the `MUSHAF_PAGE_COLOR` with opacity set by `MUSHAF_PAGE_OPACITY`.
- [ ] All instances of `MUSHAF_PAGE_BACKGROUND_COLOR` are successfully renamed to `MUSHAF_PAGE_COLOR`.
- [ ] Users can adjust `MUSHAF_PAGE_OPACITY` using a slider in the Config UI.
