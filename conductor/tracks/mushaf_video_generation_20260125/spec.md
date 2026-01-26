# Specification: Mushaf Video Generation Feature

## Overview
This feature allows users to generate recitation videos that display the Quran in a traditional Mushaf layout. Users can select a Surah, a reciter, and a background (image or video) using the existing background selection module. The generated video will render multiple Mushaf lines simultaneously, with the active line being read by the reciter visually highlighted.

## Functional Requirements

### 1. New Interface: Mushaf Video Creator
- A new web page/interface where users can:
    - Select a Surah from a dropdown.
    - Select a Reciter from a dropdown (using the same source as the Word-by-Word page).
    - Access the integrated Background Selection Module (Unsplash, Pexels, Upload, Reset).
    - Configure the number of visible lines (Default: 15).

### 2. Video Rendering Logic (MoviePy)
- **Mushaf Layout Integration:** Use the mapping logic from `db_ops/crud_mushaf.py` to retrieve line boundaries and Arabic glyphs.
- **Dynamic Line Management:**
    - Render a "window" of lines (default 15).
    - If the number of lines is less than 15, handle paging or scrolling as the reciter progresses.
- **Active Line Highlighting:**
    - Retrieve word-level timestamps from the WBW databases to determine which line is currently being read.
    - Apply a semi-transparent background highlight or soft glow behind the active line.
- **Overlay Elements:**
    - **Header:** "Bismillah" at the start of the recitation.
    - **Footer:** Display Surah Name, current Ayah number, and Reciter Name.
    - **Progress:** A progress bar indicating the completion of the recitation.

### 3. Data Sourcing
- **Recitation:** Use the Word-by-Word databases for recitation audio and timestamps.
- **Structure:** `qpc-v2-15-lines.db` for Mushaf structure.
- **Content:** `word_by_word_qpc-v2.db` for Arabic glyphs.
- **Fonts:** Page-specific QPC v2 fonts from `QPC_V2_Font.ttf`.

## Non-Functional Requirements
- **Configurability:** The number of lines displayed per "scene" must be a configurable parameter passed to the generator.
- **Performance:** Handle the rendering of multiple text lines efficiently within MoviePy.

## Acceptance Criteria
- [ ] Users can navigate to the Mushaf Video section and select Surah/Reciter/Background.
- [ ] The generated video shows the specified number of Mushaf lines.
- [ ] The active line correctly highlights in sync with the recitation audio.
- [ ] Footer information (Surah, Ayah, Reciter) and progress bar are visible and accurate.
- [ ] The "Bismillah" header appears at the beginning of the video.

## Out of Scope
- Word-level highlighting within the Mushaf lines (initially focusing on line-level highlights).
- Implementing transition animations between lines (focusing on discrete highlighting).
