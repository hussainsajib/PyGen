# Specification: Mushaf Video Border Toggle

## Overview
This track implements a global configuration setting to toggle the visibility of the decorative border in Mushaf video generation. Users will be able to enable or disable the border for both regular videos and Shorts through the web interface.

## Functional Requirements
- **Configuration Key:** Add a new configuration key `MUSHAF_BORDER_ENABLED` to the system.
- **Default Value:** The border should be **disabled (False)** by default.
- **Web Interface:** Add a checkbox to the `/config` page that allows users to toggle `MUSHAF_BORDER_ENABLED`.
- **Conditional Rendering:** Update the Mushaf video generation engine to conditionally render the border based on the `MUSHAF_BORDER_ENABLED` setting.
- **Consistency:** Ensure the toggle affects both regular Mushaf videos and Mushaf Shorts.

## Non-Functional Requirements
- **Performance:** Conditional check for the border should not noticeably impact video generation time.
- **Simplicity:** The implementation should strictly focus on the toggle and not alter other aspects of the Mushaf layout or rendering logic.

## Acceptance Criteria
- A checkbox for "Mushaf Border Enabled" exists on the `/config` page.
- Changing the checkbox state updates the `MUSHAF_BORDER_ENABLED` value in the database.
- When `MUSHAF_BORDER_ENABLED` is False, generated Mushaf videos (both regular and Shorts) do NOT show the decorative border.
- When `MUSHAF_BORDER_ENABLED` is True, generated Mushaf videos show the decorative border as before.

## Out of Scope
- Individual toggles for regular vs. Shorts videos.
- Customization of border styles or colors.
- Changes to the border width (this was handled in a previous track).
