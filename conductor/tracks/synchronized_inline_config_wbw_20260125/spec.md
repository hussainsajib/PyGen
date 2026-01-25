# Specification: Synchronized Inline Configuration on WBW Page

## Overview
Enhance the "Word-by-Word" video creation interface by adding direct controls for core generation settings: Language and Social Media Uploads (YouTube/Facebook). This eliminates the need to navigate back and forth to the main Configuration page for routine adjustments. These controls will synchronize directly with the global application configuration in the database.

## Functional Requirements

### 1. Inline Controls on `wbw.html`
- **Language Selection:**
    - Add a dropdown menu to select the video generation language.
    - On page load, it must default to the current `DEFAULT_LANGUAGE` value from the database.
    - It should list all languages currently supported in the `languages` database table.
- **Upload Toggles:**
    - Add two toggles (switches): "Upload to YouTube" and "Upload to Facebook".
    - These must reflect the current state of `UPLOAD_TO_YOUTUBE` and `ENABLE_FACEBOOK_UPLOAD` config keys on load.

### 2. Global Synchronization
- **Backend Persistence:**
    - Implement an API endpoint (or reuse existing ones) to update specific configuration keys via `POST` or `PATCH` requests.
    - When a user changes the language dropdown or toggles an upload switch on the WBW page, an asynchronous request (AJAX/Fetch) must be sent to the backend to update the database immediately.
- **Cross-Page Consistency:**
    - Since these updates modify the global database, the main Configuration page (`/config`) will automatically display the new values upon its next reload.

### 3. User Feedback
- Provide a subtle visual indicator (e.g., a brief fade or a small checkmark) when a setting is successfully synchronized with the backend.

## Non-Functional Requirements
- **Workflow Efficiency:** The synchronization should be fast enough that it doesn't hinder the user from immediately clicking "Generate Video".
- **Responsive Design:** The new controls must integrate into the existing mobile-optimized layout of the WBW page without breaking the grid.

## Acceptance Criteria
- [ ] Language dropdown on WBW page correctly initializes with the current global default.
- [ ] Changing the language on the WBW page updates the `DEFAULT_LANGUAGE` config in the database.
- [ ] YouTube and Facebook toggles on WBW page initialize with current global settings.
- [ ] Toggling YouTube/Facebook settings on the WBW page updates `UPLOAD_TO_YOUTUBE` and `ENABLE_FACEBOOK_UPLOAD` in the database.
- [ ] Changes made on the WBW page are reflected on the `/config` page after a refresh.

## Out of Scope
- Real-time WebSocket updates to the Config page (database persistence is sufficient).
- Adding these controls to other generation pages (e.g., Surah, Tafseer) at this time.
