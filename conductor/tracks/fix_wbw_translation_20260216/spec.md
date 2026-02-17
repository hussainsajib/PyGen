# Specification: Fix Missing Full Ayah Translation in WBW Videos

## Overview
This track addresses a bug where the full ayah translation is not rendered at the bottom of the screen in Word-by-Word (WBW) videos, even when `WBW_FULL_TRANSLATION_ENABLED` is set to `True`. This is a regression from previous functionality.

## Functional Requirements
- **Visibility:** The full ayah translation must be visible at the bottom of the screen for the entire duration of the ayah's playback.
- **Configuration:** Respect the `WBW_FULL_TRANSLATION_ENABLED` toggle.
- **Source Selection:** Use the database specified in `WBW_FULL_TRANSLATION_SOURCE` or fall back to the language's default full translation database.
- **Styling:** The translation should be legible, ideally with a semi-transparent background box to separate it from the video background.
- **Universal WBW Support:** Must work across all WBW rendering paths (Advanced WBW, standard WBW, and interlinear).

## Non-Functional Requirements
- **Performance:** Ensure that fetching and rendering the extra text clip does not significantly impact video generation time.

## Acceptance Criteria
1. Generate a WBW video (e.g., for Surah 1, Reciter Maher Al Muaiqly) with `WBW_FULL_TRANSLATION_ENABLED` set to `True`.
2. Verify that the full ayah translation appears at the bottom of the screen.
3. Verify that the translation matches the expected text from the configured translation database.
4. Verify that the styling (position, font size, background) is consistent with the app's design.

## Out of Scope
- Changing the layout for non-WBW videos.
- Modifying the actual translation text in the databases.
