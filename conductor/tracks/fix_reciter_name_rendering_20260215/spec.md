# Specification: Fix Reciter Name Rendering in Footer

## Overview
The user reports that the reciter's name in the video footer (left side) is not displayed correctly ("letters are not properly shown"). This issue likely stems from incorrect complex text layout (CTL) rendering for Bengali/Arabic scripts when using `Pillow` or `MoviePy` on the Windows environment. The goal is to ensure that the reciter's name (and other footer text) is rendered with correct shaping and ligature support.

## Context
- **Affected Area:** Footer of the Mushaf video (Left side - Reciter Name).
- **Reported Issue:** "Letters are not properly shown" (implies disjointed characters or incorrect rendering of complex scripts like Bengali).
- **Rendering Engine:** `MushafRenderer` (uses `Pillow`'s `ImageDraw.text`) and `MoviePy`'s `TextClip`.
- **Font:** `kalpurush.ttf` (standard Bengali font).

## Reproduction
- Generate a video with a Bengali reciter name (e.g., "মিশারি আল-আফাসি").
- Observe the footer. The characters might be separated (e.g., "ম ি শ া র ি") instead of combined ("মিশারি").

## Requirements

### Functional Requirements
1.  **Complex Script Support:** The rendering pipeline must correctly shape and render complex scripts (Bengali, Arabic) in the footer.
2.  **Font Validation:** Ensure `kalpurush.ttf` is correctly loaded and supports the required glyphs.
3.  **Shaping Library:** If `Pillow`'s default layout engine is insufficient, integrate a text shaping library (like `uharfbuzz` or `pyribs`?) or configure `Pillow` to use `libraqm` if possible (hard on Windows without pre-built wheels).
    - **Alternative:** Use a python-based shaping library like `bidi` + `arabic_reshaper` (for Arabic) or find a solution for Bengali.
    - **Better Alternative:** `libraqm` is the standard for Pillow. If unavailable, we might need to use `pango` or `cairo`? No, stick to Python/Pillow if possible.
    - **Workaround:** If `Pillow` fails, maybe `MoviePy`'s `TextClip` (via ImageMagick) handles it better? But `MushafRenderer` uses `Pillow` directly for performance.

### Implementation Constraints
- The solution must work within the existing `MushafRenderer` (fast engine) and `single_clip` (standard engine).
- **Environment:** Windows (win32). `libraqm` might be tricky.

## Success Criteria
- The reciter name "মিশারি আল-আফাসি" (and others) appears correctly joined and shaped in the output video footer.
