# Plan: Facebook Video Integration

This plan outlines the steps to implement a modular Facebook video upload feature, mirroring the existing YouTube integration.

## Phase 1: Foundation & Configuration
- [x] Task: Define Facebook credentials in environment variables (`FB_PAGE_ACCESS_TOKEN`, `FB_PAGE_ID`).
- [x] Task: Update `ConfigManager` in `config_manager.py` to include `ENABLE_FACEBOOK_UPLOAD`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Foundation & Configuration' (Protocol in workflow.md)

## Phase 2: Facebook API Integration Module
- [x] Task: Create `processes/facebook_utils.py` with a basic Facebook API client using `httpx` or `requests`.
- [x] Task: Implement `upload_standard_video` function in `facebook_utils.py`.
- [x] Task: Implement `upload_reel` function in `facebook_utils.py` (using the Reels API endpoint).
- [x] Task: Implement a unified `upload_to_facebook` entry point that decides between Reels and Standard videos based on aspect ratio and duration.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Facebook API Integration Module' (Protocol in workflow.md)

## Phase 3: Pipeline Integration
- [x] Task: Identify the post-generation hook where YouTube uploads are triggered (likely in `app.py` or a background worker).
- [x] Task: Integrate the Facebook upload call into the background worker logic, ensuring it respects the `ENABLE_FACEBOOK_UPLOAD` flag.
- [x] Task: Add logging for Facebook upload status (Success/Failure/Skipped).
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Pipeline Integration' (Protocol in workflow.md)

## Phase 4: Verification & UI Feedback
- [x] Task: Verify that metadata from `.txt` files is correctly parsed and passed to Facebook.
- [x] Task: (Optional) Add status indicators in the Manual Upload UI for Facebook upload status if feasible within the current dashboard structure.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Verification & UI Feedback' (Protocol in workflow.md)
