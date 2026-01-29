# Specification: Mushaf Video Configurable Border Width

## 1. Overview
**Type:** Feature / Visual Refinement
**Goal:** Make the width of the decorative border in Mushaf videos configurable via the application settings and reduce the default width by 20% compared to the previous hardcoded value.

## 2. Functional Requirements
- **Configurable Width:** Introduce a new configuration setting `MUSHAF_BORDER_WIDTH_PERCENT` to control the width of the Mushaf page border relative to the total video width.
- **Default Value:** The default value for this setting should be `40` (representing 40% of the screen width), which is effectively 20% narrower than the previous hardcoded 50%.
- **Valid Range:** The setting should accept integer values between `10` and `90` (percentage).
- **UI Integration:** The setting must be adjustable via a slider in the `/configs` dashboard.

## 3. Implementation Details
- **Configuration:** Add `MUSHAF_BORDER_WIDTH_PERCENT` to `config_manager.py` and the database with a default of `40`.
- **Frontend:** Add a range slider for `MUSHAF_BORDER_WIDTH_PERCENT` in `templates/config.html`.
- **Rendering Logic:**
    - Modify `factories/single_clip.py` (specifically `generate_mushaf_page_clip`).
    - Replace the hardcoded `border_w = int(width * 0.50)` with dynamic logic using the config value: `border_w = int(width * (config_val / 100))`.

## 4. Acceptance Criteria
- [ ] `MUSHAF_BORDER_WIDTH_PERCENT` exists in the database with a default of 40.
- [ ] Users can adjust the border width percentage via the web UI.
- [ ] Generated videos reflect the configured border width.
- [ ] The default visual result is a border that occupies 40% of the screen width.
