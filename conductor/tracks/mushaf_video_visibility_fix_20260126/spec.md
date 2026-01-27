# Specification: Mushaf Video Header and Basmallah Visibility Fix

## Overview
Fix issues in the Mushaf video generator where the Basmallah is incorrectly highlighted and both the Surah header and Basmallah disappear prematurely. These elements should remain visible for the entire duration of the page/scene.

## Functional Requirements
- **Disable Basmallah Highlighting:** Ensure that lines of type `basmallah` are never highlighted, regardless of the recitation timestamps.
- **Persistent Visibility:**
    - The Surah header and Basmallah must remain visible for the entire duration of the scene/page where they are rendered.
    - **Implementation Logic:** Set the `end_ms` for `surah_name` and `basmallah` lines to match the `end_ms` of the last Ayah on that specific page/scene.

## Non-Functional Requirements
- **Visual Consistency:** The headers and Basmallah should provide a stable reference at the top of the page without flickering or disappearing.
- **Maintainability:** Use the existing line-type logic to apply these fixes.

## Acceptance Criteria
1. Basmallah is visible but never highlighted during recitation.
2. Surah header and Basmallah remain visible until the video transitions to the next page/scene.
3. No regressions in standard Ayah highlighting or alignment.

## Out of Scope
- Integration of these visibility rules into the non-Mushaf (Word-by-Word Interlinear) generator.
- Customizing the visual style of the headers or Basmallah.
