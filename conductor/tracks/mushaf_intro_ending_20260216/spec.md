# Specification: Intro and Ending Screens for Mushaf Videos

## Overview
This track introduces dedicated 5-second intro and ending screens for both standalone Mushaf and Juz Mushaf videos. These screens will provide essential context (Surah/Para name, Reciter) and branding (Taqwa Bangla, Subscribe request) while maintaining visual continuity by using the same background and effects as the main recitation.

## Requirements

### 1. Functional Requirements
- **Intro Screen (5 seconds):**
    - **Content:** Large Bengali name of the Surah (for standalone) or "পারা X" (for Juz) centered horizontally and vertically.
    - **Sub-heading:** Reciter's Bengali name centered below the main heading.
    - **Localization:** Use Bengali digits for Surah/Para numbers.
- **Ending Screen (5 seconds):**
    - **Content:** Brand name "তাকওয়া বাংলা" centered.
    - **Sub-heading:** A call to action: "চ্যানেলটি সাবস্ক্রাইব করুন" (Please subscribe to the channel).
- **Background Continuity:** Both screens must use the active background (image or looped video) and respect the `MUSHAF_BACKGROUND_DIMMING` setting.
- **Engine Support:** Integrate these screens into both the standard MoviePy engine and the high-speed Fast rendering engines.

### 2. Technical Requirements
- **Rendering Method:** Render these screens as part of the main video generation sequence (integrated approach) to ensure high-performance encoding in Fast engines.
- **Typography:** Use the standard project font (Kalpurush) for all Bengali text.
- **Asset Sourcing:** Reuse the background generation logic from `factories/single_clip.py`.
- **Timing:** Account for the additional 10 seconds in the total video duration and progress bar calculations.

## Success Criteria
- [ ] Every generated Mushaf and Juz video starts with the correct intro screen.
- [ ] Every video ends with the standardized branding screen.
- [ ] Text on both screens is properly shaped (Bengali CTL) and centered.
- [ ] Background dimming is correctly applied to these screens if enabled.
- [ ] The feature works seamlessly across Standard, FFmpeg, and OpenCV engines.
