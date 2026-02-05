# Specification: Juz-Based Mushaf Video Generation

## Overview
This feature introduces the capability to generate long-form Mushaf-style recitation videos for entire Juz of the Quran. Unlike the current Surah-based workflow, this system will automatically determine Juz boundaries, concatenate audio across multiple Surahs, and handle complex transitions (headers and Basmallah) within a continuous 15-line Mushaf layout.

## Goals
- Provide a dedicated user interface for selecting a Juz and reciter.
- Automate the assembly of audio and word-by-word timestamps for multi-Surah segments.
- Maintain visual parity with the existing Mushaf video engine (borders, backgrounds, progress bars).

## Functional Requirements

### 1. Juz Discovery and Boundaries
- Retrieve Juz start/end points (Surah and Ayah numbers) from `databases/text/quran-metadata-juz.sqlite`.
- Iterate through all Surahs contained within the selected Juz.

### 2. UI Development
- Create a new web interface `/juz-video` featuring:
    - Juz Number selection (1-30).
    - Reciter selection (sharing the reciter list from Mushaf video).
    - Visible lines per page configuration.
    - Format toggle (Vertical/Short vs. Horizontal/Standard).
    - Integrated background selector (Unsplash/Pexels/Local).
    - Page background mode and opacity controls.
    - YouTube upload settings.

### 3. Audio and Timing Engine
- **On-the-Fly Juz Audio:** Concatenate Surah-level audio files into a single Juz audio stream.
- **Basmallah Injection:**
    - Inject Basmallah audio at the start of every Surah within the Juz (excluding Surah 1 and Surah 9).
    - **Surah At-Tawbah Exception:** Insert a 5-second silence gap instead of Basmallah.
- **Timestamp Mapping:** Offset all word-by-word timestamps for the Juz based on the cumulative duration of preceding Surahs and injected Basmallah/gaps.

### 4. Rendering Logic (Mushaf Page)
- **Injection Transition Logic:** Seamlessly transition between Surahs within the 15-line Mushaf flow.
- Inject Surah headers and Basmallah ligatures into the line list at the exact Ayah transition points.
- Ensure the progress bar remains continuous across the entire Juz duration.

### 5. YouTube Metadata Generation
- **Automated Chapter Markers:** Generate a list of timestamps and Surah names for the video description.
- **Localized Titles:** Use a pattern like "Juz [Number] Full - [Reciter Name]".
- **Hashtags:** Include Juz-specific tags (e.g., #Juz1, #FullJuz).

## Non-Functional Requirements
- **Performance:** Ensure audio concatenation and timestamp offsetting are handled efficiently before the MoviePy encoding phase.
- **UI Consistency:** Use Bootstrap 5 and the project's "Modern and Bold" aesthetic.

## Acceptance Criteria
- [ ] A Juz video can be successfully generated starting from Juz 1 Ayah 1 to the end of the Juz.
- [ ] Surah transitions include the correct header and Basmallah (or 5s gap for Surah 9).
- [ ] Word-level highlighting remains perfectly synchronized even after Surah boundaries.
- [ ] The YouTube description automatically contains clickable chapter markers for each Surah.

## Out of Scope
- Multi-language support (defaulting to project standard).
- Generating videos for arbitrary Ayah ranges that don't align with Juz boundaries.
