# Specification: Bengali Localization for Juz Videos (Para Labels and Metadata)

## Overview
This track focuses on improving the Bengali localization for Juz-based Mushaf videos. It replaces the "Juz" label with "পারা" (Para) in the video footer and updates the YouTube/Facebook metadata (titles and descriptions) to follow a standardized Bengali format.

## Functional Requirements

### 1. Footer Label Rebrand
- **Target:** Juz Mushaf videos (both standard and high-speed).
- **Change:** In the video footer, replace the label `Juz [Number]` with `পারা [Bengali Number]`.
- **Format:** `পারা ১`, `পারা ২`, etc., using Bengali digits for the number.

### 2. Video Metadata Update (YouTube & Facebook)
- **Target:** Metadata files generated for Juz videos.
- **Title Format:** `কুরআন তিলাওয়াত - পারা [Bengali Number] - [Bengali Reciter Name]`
- **Description Format:** Ensure the description also uses "পারা" instead of "Juz" when referring to the content.
- **Localization:** All numbers in the metadata related to the Para must be in Bengali digits.

## Technical Requirements
- Update `processes/mushaf_video.py` and `processes/mushaf_fast_video.py` to use the localized "Para" label for Juz videos when the language is Bengali.
- Update `processes/description.py` (specifically `generate_juz_details`) to implement the new Bengali title and description format.
- Utilize existing Bengali digit conversion utilities (e.g., from `bangla` package or custom utility in `factories/single_clip.py`).

## Acceptance Criteria
- [ ] For a Juz 1 video, the footer displays "পারা ১".
- [ ] The generated metadata file for Juz 1 shows the title: "কুরআন তিলাওয়াত - পারা ১ - [কারি নাম]".
- [ ] Facebook and YouTube upload details reflect the new localized format.
- [ ] Standalone Surah videos remain unaffected.
