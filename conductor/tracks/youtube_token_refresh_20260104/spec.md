# Specification: YouTube Channel Token Refresh Utility

## Overview
Implement a user-friendly mechanism within the Config UI to allow manual refreshing of YouTube access tokens for specific channels (languages). This will address `invalid_grant` errors and ensure seamless re-authentication when tokens expire or are revoked.

## Functional Requirements

### 1. UI Enhancements (Config Page)
- **Refresh Button:** Add a "Refresh YouTube Token" button to the `config.html` template next to each configured language entry that has a `youtube_channel_id`.
- **User Feedback:** Provide clear visual feedback during the refresh process (e.g., loading spinner) and upon completion (e.g., success/error message).

### 2. Backend API Integration
- **New Endpoint:** Create a new API endpoint (e.g., `/youtube/refresh-token`) in `app.py` that accepts the language ID.
- **Token Handling Logic:**
    - The endpoint will fetch the `youtube_channel_id` associated with the provided language ID from the database.
    - It will then trigger the Google OAuth re-authentication flow in the user's browser for that specific channel.
    - Upon successful re-authentication, the old token in `client_info.json` will be overwritten with the new, valid token (including a refresh token).

### 3. Authentication Flow
- **Re-authentication Trigger:** The system will open a browser window to guide the user through the Google OAuth consent flow.
- **Persistent Tokens:** The flow must ensure that a new refresh token is obtained. This might require `access_type='offline'` and `prompt='consent'` in the OAuth flow parameters.

## Non-Functional Requirements
- **Security:** Ensure that API keys and client secrets are not exposed on the frontend.
- **Error Handling:** Gracefully handle network issues, invalid language IDs, or failed authentication attempts.
- **User Experience:** The re-authentication process should be as smooth and intuitive as possible.

## Acceptance Criteria
- [ ] A "Refresh YouTube Token" button is visible for each language with a configured `youtube_channel_id` on the `/config` page.
- [ ] Clicking the button initiates the Google OAuth flow in a new browser window.
- [ ] After completing the OAuth flow, the new token is successfully saved to `client_info.json`.
- [ ] Subsequent YouTube uploads for that language use the newly refreshed token without `invalid_grant` errors.
- [ ] The refresh process provides clear feedback to the user.

## Out of Scope
- Automated background token refreshing (this feature focuses on manual trigger).
- Refreshing tokens for Facebook or other services.
