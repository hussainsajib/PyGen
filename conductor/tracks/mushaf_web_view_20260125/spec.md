# Specification: Mushaf Web View Feature

## Overview
This feature introduces a new web-based interface for viewing the Quran in a traditional 15-line Mushaf layout. Users will be able to navigate to a specific page number and see the corresponding text rendered with page-specific fonts, maintaining the structural integrity of the Mushaf.

## Functional Requirements

### 1. New Web Endpoint (`/mushaf`)
- A new route `/mushaf` will be added to the FastAPI application.
- The page will initially load with a default page (e.g., Page 1).
- The user can select a page number (1-604) using a dropdown menu or a numerical slider.

### 2. Mushaf Layout Rendering
- The layout will consist of exactly 15 lines (or as many as defined for the page in the database).
- Each line will be an individual HTML element (e.g., a `div`).
- The text will be centered and displayed on a cream-colored background (`rgb(255, 255, 245)`).
- The words within each line will be fetched from the `word_by_word_qpc-v2.db` based on the mapping logic established in the analysis report.

### 3. Dynamic Font Loading
- The application will serve the page-specific `.ttf` fonts from the `QPC_V2_Font.ttf` folder.
- CSS `@font-face` will be used to dynamically load the font corresponding to the current page (e.g., `font-family: 'Page1Font'; src: url('/static/fonts/p1.ttf');`).

### 4. Navigation
- In addition to the selection menu, the page should provide basic "Previous" and "Next" controls for intuitive browsing.

## Data Integration
- **Structure:** `qpc-v2-15-lines.db` (Table: `pages`) will be used to determine line boundaries and page metadata.
- **Content:** `word_by_word_qpc-v2.db` (Table: `words`) will provide the Arabic glyphs for each word.
- **Fonts:** Page-specific files in `QPC_V2_Font.ttf/p{n}.ttf`.

## Acceptance Criteria
- [ ] Users can access `/mushaf` and see Page 1 rendered correctly.
- [ ] Changing the page number via the UI updates the content and the font immediately.
- [ ] The text layout accurately reflects the 15-line Mushaf structure.
- [ ] Arabic glyphs are rendered without "empty boxes" using the correct fonts.

## Out of Scope
- Implementing word-by-word highlighting or audio playback in this initial version.
- Mobile-specific optimizations beyond basic responsiveness.
- Multi-mushaf style support (sticking to the 15-line QPC v2 layout).
