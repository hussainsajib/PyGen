# Implementation Plan: Multi-Language YouTube Channel Integration

## Phase 1: Database & Token Storage
- [x] Task: Expand Language model with YouTube Channel ID
    - [x] Sub-task: Add `youtube_channel_id` column to `Language` model in `db/models/language.py`.
    - [x] Sub-task: Create a migration script to add the column.
- [x] Task: Seed Language table with YouTube Channel IDs
    - [x] Sub-task: Update `scripts/init_languages.py` (or create a new script) to seed `youtube_channel_id` for Bengali and English languages. (Requires user to provide actual YouTube Channel IDs).
- [x] Task: Refactor YouTube token management
    - [x] Sub-task: Modify `processes/youtube_utils.py` to use `client_info.json` as a structured token store (dictionary of {channel_id: token_data}).
    - [x] Sub-task: Implement logic to load/save specific token data from `client_info.json` based on the target `youtube_channel_id`.
- [~] Task: Conductor - User Manual Verification 'Phase 1: Database & Token Storage' (Protocol in workflow.md)

## Phase 2: Dynamic Authentication & Upload [checkpoint: eb19290]
- [~] Task: Update YouTube authentication process
    - [ ] Sub-task: Modify `processes/youtube_utils.py` to acquire and refresh tokens specifically for the `youtube_channel_id` associated with the active language.
    - [ ] Sub-task: Implement a mechanism to prompt for re-authentication if a token is invalid or expired for a specific channel.
- [x] Task: Refactor upload logic to use localized channel
    - [x] Sub-task: Update `processes/processes.py` (`create_wbw_video_job`, `create_surah_video`, `manual_upload_to_youtube`) to fetch the `youtube_channel_id` from the `Language` model based on `DEFAULT_LANGUAGE`.
    - [x] Sub-task: Pass the target `youtube_channel_id` to `processes/youtube_utils.py`'s upload functions.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Dynamic Authentication & Upload' (Protocol in workflow.md)

## Phase 3: Integration & Final Verification
- [~] Task: End-to-End Verification - Bengali Channel
    - [ ] Sub-task: Generate a video with `DEFAULT_LANGUAGE` set to Bengali and `UPLOAD_TO_YOUTUBE` enabled.
    - [ ] Sub-task: Verify the video is uploaded to the "Taqwa Bangla" channel.
- [ ] Task: End-to-End Verification - English Channel
    - [ ] Sub-task: Generate a video with `DEFAULT_LANGUAGE` set to English and `UPLOAD_TO_YOUTUBE` enabled.
    - [ ] Sub-task: Verify the video is uploaded to the "Taqwa" channel.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Integration & Final Verification' (Protocol in workflow.md)
