# Plan: YouTube Channel Token Refresh Utility

This plan outlines the steps to add a UI-driven token refresh mechanism for YouTube channels.

## Phase 1: Backend API Enhancement
- [x] Task: Create new endpoint in `app.py`.
    - [x] Sub-task: Create `tests/test_youtube_refresh_route.py` with failing tests for the `/youtube/refresh-token` endpoint.
    - [x] Sub-task: Implement `/youtube/refresh-token` route that accepts `language_id`.
    - [x] Sub-task: Within the route, retrieve `youtube_channel_id` from the `Language` model using `language_id`.
    - [x] Sub-task: Call a new `refresh_channel_token` function in `processes/youtube_utils.py` with the `youtube_channel_id`.
- [x] Task: Implement token refresh logic in `processes/youtube_utils.py`.
    - [x] Sub-task: Create `refresh_channel_token(channel_id)` function.
    - [x] Sub-task: This function should initiate the OAuth flow for the given `channel_id`, ensuring `access_type='offline'` and `prompt='consent'`.
    - [x] Sub-task: On successful authentication, it should save the new token to `client_info.json`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Backend API Enhancement' (Protocol in workflow.md)

## Phase 2: Frontend UI Implementation
- [x] Task: Update Config UI (`templates/config.html`).
    - [x] Sub-task: Add a "Refresh YouTube Token" button for each language with a configured `youtube_channel_id`.
    - [x] Sub-task: Implement JavaScript to handle the button click, make an API call to `/youtube/refresh-token` with the `language_id`, and handle the browser redirect for OAuth.
    - [x] Sub-task: Display appropriate feedback (e.g., "Redirecting for authentication...", "Token refreshed successfully!").
- [x] Task: Conductor - User Manual Verification 'Phase 2: Frontend UI Implementation' (Protocol in workflow.md)

## Phase 3: Final Integration & E2E Testing
- [x] Task: Perform End-to-End Verification.
    - [x] Sub-task: Log into the UI, go to the Config page.
    - [x] Sub-task: Click "Refresh YouTube Token" for a channel (e.g., English or Bengali).
    - [x] Sub-task: Complete the OAuth flow in the browser.
    - [x] Sub-task: Verify that the old token for that channel is gone from `client_info.json` and a new one exists (check its `expiry` and `refresh_token` fields).
    - [x] Sub-task: Generate and upload a video using the refreshed channel to confirm it works.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Final Integration & E2E Testing' (Protocol in workflow.md)
