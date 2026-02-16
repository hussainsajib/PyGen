# Specification: Fix Arabic Word Ordering in High-Speed Rendering Engines

## Overview
This track addresses a visual regression in the high-speed "Fast" video engines (FFmpeg, OpenCV, PyAV) where Arabic words in Mushaf-style videos are being arranged from left-to-right (LTR) instead of the authentic right-to-left (RTL) flow. The fix involves ensuring that the word sequence for every rendered line is manually reversed before being joined and passed to the image drawing library (Pillow).

## Requirements

### 1. Functional Requirements
- **Correct RTL Word Sequence:** In every Mushaf line, words must be ordered from right to left across the screen.
- **Authentic Word Placement:** The first word of an Ayah line (or header) must be positioned at the far right of the content area.
- **Engine Parity:** The visual output of the Fast engines must match the correct RTL arrangement used in the standard MoviePy engine.

### 2. Technical Requirements
- **Logic Update:** Modify `factories/mushaf_fast_render.py` to reverse the word list retrieved from the database before string concatenation.
- **Shared Logic Alignment:** Verify if `factories/single_clip.py` (which contains shared static page rendering logic) also requires this adjustment to maintain consistency across backends.
- **Preserve Character Order:** Ensure that while word *order* within a line is reversed, the internal character sequence *within* each word (especially for multi-glyph QPC v2 symbols) remains correct.

## Success Criteria
- [ ] Every line in a high-speed generated Mushaf or Juz video follows the correct RTL word flow.
- [ ] Visual verification confirms that Word 1 of a line is on the right side.
- [ ] No regression in glyph shapes or connections.
