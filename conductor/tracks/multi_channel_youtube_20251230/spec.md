# Track Specification: Multi-Language YouTube Channel Integration

## Overview
This track integrates language-specific YouTube channel management into the system. When the `DEFAULT_LANGUAGE` is set, videos generated in that language will automatically target the corresponding YouTube channel for upload, using separate authentication tokens for each channel.

## Functional Requirements
- **Channel Association:**
    - The `languages` table will be updated to include a `youtube_channel_id` column, associating each language (e.g., English, Bengali) with its default YouTube channel ID.
- **Dynamic YouTube Token Management:**
    - The system will manage multiple YouTube authentication tokens, one for each channel/language.
    - Tokens will be stored in a single `client_info.json` file, structured as a dictionary where keys are channel identifiers (e.g., language names or channel IDs) and values are the token data.
    - When a video is uploaded, the correct token will be selected based on the `DEFAULT_LANGUAGE` or the associated `youtube_channel_id`.
- **Language-Specific Uploads:**
    - Videos generated with `DEFAULT_LANGUAGE` set to Bengali will be uploaded to the "Taqwa Bangla" channel.
    - Videos generated with `DEFAULT_LANGUAGE` set to English will be uploaded to the "Taqwa" channel.

## Technical Requirements
- **Database Schema:**
    - Migration: Add `youtube_channel_id` column to `languages` table.
    - Seeding: Update `languages` table with appropriate YouTube Channel IDs for "Taqwa Bangla" (Bengali) and "Taqwa" (English).
- **Authentication Refactoring:**
    - Modify `processes/youtube_utils.py` to handle loading and saving tokens from the structured `client_info.json` file.
    - Update the authentication flow to require separate one-time authentications for each channel to generate the initial tokens.
    - The system must refresh tokens as needed, storing them back in the correct location within `client_info.json`.
- **Upload Logic Refactoring:**
    - Update `processes/processes.py` and other relevant upload logic to fetch the `youtube_channel_id` based on the selected `DEFAULT_LANGUAGE` and use the corresponding token for authentication during upload.

## Acceptance Criteria
- [ ] When `DEFAULT_LANGUAGE` is 'bengali', videos are successfully uploaded to the specified Bengali YouTube channel.
- [ ] When `DEFAULT_LANGUAGE` is 'english', videos are successfully uploaded to the specified English YouTube channel.
- [ ] The `client_info.json` file is correctly managed for multiple channel tokens.
- [ ] The `languages` table stores the `youtube_channel_id` for each language.

## Out of Scope
- Creating new YouTube channels via the application.
- Managing YouTube channel ownership or permissions.
- Complex error handling for failed YouTube authentications beyond existing retry mechanisms.
