# Plan: Synchronized Inline Configuration on WBW Page

This plan outlines the steps to add inline configuration controls (Language, YouTube/Facebook upload) to the Word-by-Word page and synchronize them with the global application settings.

## Phase 1: Backend Infrastructure (API) [checkpoint: be628d8]
- [x] Task: Write unit tests for an API endpoint that allows updating specific configuration keys.
- [x] Task: Implement or extend a route (e.g., `POST /config/set`) to handle asynchronous configuration updates from the frontend.
- [x] Task: Verify that the configuration service correctly updates the database and the in-memory cache.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Backend Infrastructure (API)' (Protocol in workflow.md) be628d8
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Backend Infrastructure (API)' (Protocol in workflow.md)

## Phase 2: Frontend Implementation (wbw.html) [checkpoint: 045b372]
- [x] Task: Write integration tests to verify that the Word-by-Word page correctly displays and submits configuration changes.
- [x] Task: Update `templates/wbw.html` to include the Language selection dropdown and Social Media Upload switches.
- [x] Task: Implement JavaScript logic in `wbw.html` to send asynchronous `fetch` requests when settings are changed.
- [x] Task: Add visual feedback (e.g., CSS transitions or status icons) to indicate successful synchronization.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Frontend Implementation (wbw.html)' (Protocol in workflow.md) 045b372

## Phase 3: Final Integration & Verification
- [x] Task: Perform end-to-end testing: change a setting on the WBW page and verify it appears on the Config page without manual DB manipulation.
- [x] Task: Ensure the new UI elements are responsive and accessible on mobile viewports.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Integration & Verification' (Protocol in workflow.md)
