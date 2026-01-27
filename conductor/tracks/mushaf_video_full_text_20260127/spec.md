# Specification: Mushaf Video Full Text Visibility and Highlighting

## Overview
Modify the Mushaf video generation engine to ensure all Quranic text within a scene is visible at all times. Highlighting should be applied dynamically to the active line without hiding non-recited lines.

## Functional Requirements
- **Permanent Text Visibility:** All lines belonging to the current "chunk" or scene (e.g., lines 1-15 of a page) must be visible throughout the entire duration of that scene's video clip.
- **Dynamic Highlighting:**
    - Highlighting (using a semi-transparent colored block) must only be applied to the specific line being recited according to its timestamps.
    - Non-recited lines in the same scene should remain visible in their default state (unhighlighted).
- **Header and Basmallah Persistent Visibility:** Surah headers and Basmallah lines must also remain visible for the entire duration of the scene they belong to.
- **Implementation Detail:** Ensure the `ImageClip` for every line in a chunk is set to the full duration of the chunk, while only the `ColorClip` (highlight) is timed.

## Non-Functional Requirements
- **Visual Clarity:** The distinction between highlighted and non-highlighted text should be clear but aesthetically pleasing.
- **Stability:** Text positioning must remain perfectly stable; lines should not move or flicker when highlighting starts or ends.

## Acceptance Criteria
1. Generated Mushaf videos show all lines of the current scene from the start of the clip.
2. Only the active line has a visible highlighting overlay at any given timestamp.
3. Surah headers and Basmallah stay visible throughout the scene.
4. No regressions in text alignment or font rendering.

## Out of Scope
- Changing the highlighting logic for non-Mushaf (Word-by-Word Interlinear) videos.
- Customizing the highlighting color or opacity beyond existing configuration.
