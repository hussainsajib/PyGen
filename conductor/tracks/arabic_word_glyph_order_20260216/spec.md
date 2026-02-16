# Specification: Fix Arabic Word Ordering in Fast Rendering Engines

## Overview
This track addresses a regression in the high-speed "Fast" video engines (FFmpeg, OpenCV, PyAV) where Arabic words in a Mushaf line are currently being arranged in the incorrect visual order (appearing Left-to-Right instead of Right-to-Left). The fix involves ensuring that the word sequence retrieved from the database is properly processed using a Bi-Directional (Bidi) algorithm before rendering to maintain authentic RTL flow.

## Requirements

### 1. Functional Requirements
- **Correct RTL Word Sequence:** In every Mushaf line, words must be ordered from Right to Left across the screen.
- **Authentic Word Placement:** The first word of an Ayah line (or the start of a multi-surah line) must be positioned at the far right of the line's content area.
- **Engine Parity:** The visual output of the Fast engines must match the correct RTL arrangement used in the standard MoviePy engine and the web Mushaf viewer.

### 2. Technical Requirements
- **Bidi Integration:** Implement or correct the use of `python-bidi` (or a similar Bidi algorithm) in `factories/mushaf_fast_render.py` to reorder the text strings logically before they are passed to Pillow's `ImageDraw.text`.
- **String Assembly Fix:** Review and refactor the word joining logic in `MushafRenderer` to ensure strings are joined in the correct logical sequence expected by the Bidi algorithm and QPC v2 fonts.
- **Font-Aware Rendering:** Ensure that PUA (Private Use Area) glyphs and page-specific fonts continue to display correctly after Bidi reordering.

## Success Criteria
- [ ] Every line in a Juz or standalone Mushaf video follows the correct RTL word flow.
- [ ] Words with associated signs (e.g., pause signs) maintain their correct relative positions.
- [ ] Visual verification confirms that Word 1 of a line is on the right side.
