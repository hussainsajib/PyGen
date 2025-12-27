# Track Specification: Word-by-Word Interlinear Rendering

## Overview
This track introduces a new rendering mode for the Word-by-Word (WBW) video engine. Instead of displaying a single translation line for the entire verse, translations will be rendered directly beneath each corresponding Arabic word (interlinear style). Arabic words will be underlined to clearly separate them from their meanings.

## Functional Requirements
- **Interlinear Layout:**
    - Each Arabic word and its translation are treated as a single vertical block.
    - The translation text must be centered directly below its corresponding Arabic word.
    - A solid underline must be rendered beneath every Arabic word.
- **Configurable Styling:**
    - Introduce a new configuration key, `WBW_TRANSLATION_FONT_SIZE`, to control the size of the interlinear translation text.
    - Translation text should default to a significantly smaller font than the Arabic text (e.g., 60-80%).
- **Dynamic Spacing (Hybrid Approach):**
    - The horizontal spacing between word blocks must adjust to accommodate the wider element (Arabic or translation).
    - If a block exceeds a width threshold that would break the line layout, the text should be scaled down to maintain consistency.
- **Underline Style:**
    - A standard solid underline must be present under every Arabic word in the view.

## Technical Requirements
- **Engine Modification:**
    - Update `generate_wbw_advanced_arabic_text_clip` (or create a new specialized factory) in `factories/single_clip.py` to handle the interlinear layout.
    - Modify the word segmentation and placement logic in `processes/surah_video.py` or `processes/wbw_utils.py` to calculate coordinates for both Arabic and translation elements.
- **Coordinate Calculation:**
    - Implement logic to center-align translation text within the width allocated for the Arabic word block.
- **Configuration Management:**
    - Add `WBW_TRANSLATION_FONT_SIZE` with a default value to the `config` table.

## Acceptance Criteria
- [ ] Word-by-Word videos render with translations positioned directly below each Arabic word.
- [ ] Every Arabic word has a solid underline.
- [ ] Translations are centered relative to their Arabic counterparts.
- [ ] Changing `WBW_TRANSLATION_FONT_SIZE` in the `/config` UI correctly updates the video output.
- [ ] The layout remains stable and readable even with long translations or short Arabic words.

## Out of Scope
- Adding interlinear rendering to non-WBW (standard) video modes.
- Visual transitions (fades/slides) between interlinear blocks.
