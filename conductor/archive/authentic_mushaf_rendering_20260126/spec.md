# Specification: Authentic Mushaf Rendering Update

## Overview
Enhance the Traditional Mushaf Viewer in the application to render pages using structured layout data from the SQLite database, ensuring authentic typography and precise alignment according to traditional Mushaf standards.

## Functional Requirements
- **Backend Data Fetching (FastAPI):**
    - Implement/Update an endpoint **strictly for the Mushaf Viewer** to retrieve page-specific data from the layout SQLite database (`pages` table).
    - For each line on a requested page, return: `line_number`, `line_type`, `is_centered`, `surah_number`, and the concatenated text for `ayah` lines.
    - **Ayah Logic:** For `line_type: ayah`, query the `words` table to retrieve all words between `first_word_id` and `last_word_id` (inclusive) and join them in numerical order.
- **Frontend Rendering (Jinja2/HTML/CSS):**
    - **Authentic Typography:**
        - `line_type: surah_name`: Render the Surah name using `QCF_SURA.TTF`, overlaid centrally on the decorative design header rendered with `QCF_SurahHeader_COLOR-Regular.ttf`.
        - `line_type: basmallah`: Render the Bismillah using `QCF_BSML.TTF`.
        - `line_type: ayah`: Render the concatenated Quranic text using the page-specific QPC v2 fonts.
    - **Alignment & Layout:**
        - Enforce line alignment based on the `is_centered` field: `true` for centered, `false` for fully justified.
        - Maintain the 15-line grid structure as defined in the database.

## Constraints & Isolation
- **Scope Restriction:** All modifications must be isolated to the Mushaf Viewer feature (`/mushaf` route and associated components).
- **No Side Effects:** Shared utilities, global CSS, or common backend models must not be modified in any way that alters the behavior or appearance of other features (e.g., WBW rendering, video generation, dashboard).

## Acceptance Criteria
1. The Mushaf Viewer correctly displays all 15 lines per page as defined in the layout database.
2. Surah headers appear with the correct design frame and centered name text.
3. Bismillah lines use the specialized calligraphy font.
4. Quranic text lines are correctly formed and aligned (centered or justified).
5. All lines use the specified `.ttf` fonts for authentic representation.

## Out of Scope
- Modifying the Mushaf video generation engine.
- Changing global application state or shared configurations.
