# Specification: Mushaf Video Text Scaling Refinement

## 1. Overview
**Type:** Feature / Visual Refinement
**Goal:** Reduce the font size of the "normal" Quranic Arabic text (Ayahs) in Mushaf videos by 20% to improve visual balance and whitespace management.

## 2. Functional Requirements
- **Dynamic Scaling:** Introduce a new configuration setting `MUSHAF_FONT_SCALE` to control the relative size of the Arabic text.
- **Default Value:** Set the default value of `MUSHAF_FONT_SCALE` to `0.8` (representing 20% smaller than the baseline).
- **Scope:** This scaling factor applies specifically to the Arabic text rendered in the Mushaf grid (Ayah lines).
- **Layout Preservation:** The line height and 15-line grid structure will remain unchanged, resulting in increased vertical whitespace between lines for better legibility.

## 3. Implementation Details
- **Configuration:** Add `MUSHAF_FONT_SCALE` to `config_manager.py` and the database.
- **Frontend:** Add a numerical input or slider for `MUSHAF_FONT_SCALE` in the `/configs` dashboard.
- **Rendering Logic:**
    - Modify `factories/single_clip.py` (specifically `generate_mushaf_page_clip`).
    - Adjust the `font_size` calculation for "ayah" line types by multiplying it with the `MUSHAF_FONT_SCALE` value.
    - Ensure the vertical centering logic (`calculate_centered_y`) remains robust with the smaller text.

## 4. Acceptance Criteria
- [ ] Arabic Ayah text is visually 20% smaller in generated Mushaf videos.
- [ ] Increased whitespace is visible between lines.
- [ ] Line height remains constant (15 lines still fit in the same total vertical area).
- [ ] `MUSHAF_FONT_SCALE` can be updated via the dashboard and reflects in subsequent video generations.
