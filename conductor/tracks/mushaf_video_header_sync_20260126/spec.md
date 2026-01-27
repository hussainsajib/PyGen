# Specification: Mushaf Video Header Sync

## Overview
Fine-tune the rendering of Surah headers and Basmallah in Mushaf videos to achieve visual parity with the `/mushaf` web viewer, ensuring consistent scaling and positioning.

## Functional Requirements
- **Surah Header Scaling:** Adjust the font size of the Surah header ligature to match the ~15% width proportion used in the web UI.
- **Basmallah Scaling:** Keep the Basmallah smaller, matching the desired visual aesthetic (already reduced, but needs to be maintained alongside header changes).
- **Positioning:** Ensure both elements are correctly centered and spaced within the Mushaf line grid without overlapping.
- **Font Usage:** Use the local `QCF_SurahHeader_COLOR-Regular.ttf` for headers without color rendering (Pillow default).

## Acceptance Criteria
1. Surah headers in generated videos have the same relative proportions as in the web viewer.
2. Basmallah remains smaller and well-spaced.
3. No overlaps between headers, Basmallah, and the first Ayah.
4. Zero regressions in ongoing Mushaf video generation.
