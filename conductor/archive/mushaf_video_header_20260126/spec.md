# Specification: Mushaf Video Header and Basmallah Integration

## Overview
Synchronize the Mushaf video generation engine with the authentic rendering logic used in the `/mushaf` web viewer. This includes rendering the Surah header and Basmallah using specialized fonts and timing them to the start of the recitation.

## Functional Requirements
- **Authentic Rendering:**
    - **Surah Header:** Render the Surah header using `QCF_SurahHeader_COLOR-Regular.ttf` and the ligature data from `databases/text/ligatures.json`.
    - **Basmallah:** Render the Bismillah using `QCF_BSML.TTF` and character `U+00F3`.
- **Positioning:** Both elements should be centered at the very top of the scene, above the first line of Quranic text.
- **Timing Logic:**
    - The Surah header and Basmallah should only appear at the beginning of a Surah.
    - They should be visible **only while the recitation of the first Ayah (or the Bismillah itself) is active**.
- **Integration:** The rendering logic must match the final implementation of the `/mushaf` endpoint.

## Non-Functional Requirements
- **Visual Consistency:** The video output must match the aesthetic quality and layout precision of the web viewer.
- **Performance:** Rendering these additional elements should not significantly impact video generation time.

## Acceptance Criteria
1. Mushaf videos starting at Ayah 1 of any Surah display the correct decorative header.
2. The Surah header uses the `QCF_SurahHeader_COLOR-Regular.ttf` font and correct ligature.
3. The Basmallah uses the `QCF_BSML.TTF` font and `U+00F3` character.
4. Headers and Basmallah appear only during the initial recitation segment and disappear once the second Ayah begins or as defined by timestamps.
5. Zero regressions in standard Ayah rendering or alignment.

## Out of Scope
- Modifying the Word-by-Word Interlinear video generator.
- Customizing the Basmallah character beyond `U+00F3`.
