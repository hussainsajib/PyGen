# Specification: Mushaf Basmallah Resize

## Overview
Adjust the font size of the Basmallah in Mushaf-style generated videos to match the visual proportions used in the `/mushaf` web viewer.

## Functional Requirements
- **Reduced Scaling:** Decrease the font size scaling factor for `line_type: basmallah` in the video generation engine.
- **Proportional Matching:** The new scale should ensure the Basmallah height relative to regular Ayah lines matches the ~1.9x ratio found in the web UI.

## Acceptance Criteria
1. Generated Mushaf videos show a smaller Basmallah compared to the previous version.
2. The Basmallah size is visually consistent with the web viewer's implementation.
3. No regressions in Surah header sizing or standard Ayah alignment.
