# Specification: Correct Arabic Word and Glyph Ordering in Fast Rendering Engines

## Overview
This track addresses a rendering bug in the high-speed "Fast" video engines (FFmpeg, OpenCV, PyAV) where Arabic words and their associated glyphs (like pause signs) are being displayed in the incorrect visual order. Specifically, for Surah 2, Ayah 5, Word 5, the pause sign appears to the right of the word (as if rendered Left-to-Right), whereas in Arabic (Right-to-Left), the pause sign should appear to the left of the word.

## Requirements

### 1. Functional Requirements
- **Correct RTL Word Ordering:** Ensure that all words within a Mushaf line are arranged from right to left across the screen.
- **Correct Internal Glyph Ordering:** Ensure that within a single word entry, the word itself and any associated signs (pause signs, tajweed marks) are rendered in the correct logical and visual sequence for Arabic script.
- **Engine Parity:** The "Fast" rendering backends must match the correct visual output of the standard MoviePy engine.

### 2. Technical Requirements
- **Investigation:** Analyze `factories/mushaf_fast_render.py` and its interaction with `PIL.ImageDraw`.
- **Bidi Support:** Implement or fix the use of Bi-Directional (Bidi) algorithm processing for Arabic text strings before they are passed to the rendering library.
- **Reshaping:** Verify if `arabic_reshaper` is required to ensure glyphs connect and position themselves correctly when combined.
- **Font Integration:** Ensure the QPC v2 fonts are being used correctly by the Bidi/Reshaping logic to preserve custom glyph positions.

## Success Criteria
- [ ] Surah 2, Ayah 5, Word 5 displays the pause sign to the left of the word.
- [ ] Entire Ayah lines in Juz/Mushaf videos follow the correct RTL flow (start of ayah on the right).
- [ ] Text rendering remains high-fidelity without broken glyph connections.
