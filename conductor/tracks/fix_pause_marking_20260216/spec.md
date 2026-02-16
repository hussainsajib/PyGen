# Specification: Fix Pause Marking Positioning in Mushaf/Juz Videos

## Overview
In Mushaf and Juz video generation, certain Quranic words with attached pause markings (e.g., the letter 'jim') are rendering with the marking on the incorrect side. Because Arabic is a Right-to-Left (RTL) language, "after" a word means it should appear to its left. Currently, in videos, these signs appear to the right (before the word), whereas the web-based Mushaf viewer (`/mushaf` endpoint) renders them correctly.

## Functional Requirements
1. **Correct RTL Assembly:** Modify the text assembly logic in the video rendering pipeline to ensure pause markings are positioned to the left of the associated word.
2. **Engine Parity:** Ensure the fix applies to all rendering backends (MoviePy, FFmpeg, OpenCV, and PyAV).
3. **Visual Consistency:** The output in generated videos must match the correct positioning seen in the `/mushaf` web viewer.

## Acceptance Criteria
1. **Surah 110:3, Word 4:** The pause sign ('jim') must appear to the left of the word "wastagfirh".
2. **Surah 2:5, Word 5:** The pause marking must appear to the left of the word.
3. **Multi-Engine Verification:** Verification must be performed for at least the default MoviePy engine and one high-speed engine (e.g., FFmpeg).

## Out of Scope
- Changing the font itself (QPC V2).
- Modifying the web Mushaf viewer (since it is already correct).
- Adjusting timing or highlighting logic unless it is directly impacted by the text assembly change.
