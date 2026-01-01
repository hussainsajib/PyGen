# Specification: Facebook Video Integration

## Overview
Implement a modular Facebook integration that allows for automated video uploads to a Facebook Page. This feature will mirror the existing YouTube integration, allowing users to toggle it on/off and automatically upload videos (Reels or standard videos) upon generation completion.

## Functional Requirements
- **Modular Integration:** The Facebook upload logic must be contained within a new module (e.g., `processes/facebook_utils.py`) to maintain modularity and avoid tightly coupling with existing YouTube logic.
- **Configurable Uploads:** Add a new configuration setting `ENABLE_FACEBOOK_UPLOAD` (Boolean) to the `ConfigManager`.
- **Automated Upload Trigger:** If enabled, the system will automatically upload newly generated videos to the configured Facebook Page.
- **Support for Reels & Videos:** The system must determine if a video should be uploaded as a Reel (typically vertical and under 90 seconds) or a standard video based on its properties.
- **Metadata Reuse:** Use the existing localized title, description, and tags generated for YouTube for the Facebook post content.
- **Authentication:** Utilize a long-lived Page Access Token and Page ID stored in the environment configuration (`.env` or `config_manager`).

## Non-Functional Requirements
- **Error Handling:** Gracefully handle API failures (e.g., expired tokens, rate limits) without interrupting the core video generation process.
- **Logging:** Implement detailed logging for upload attempts, successes, and failures.

## Acceptance Criteria
- [ ] A new `ENABLE_FACEBOOK_UPLOAD` setting exists in the configuration.
- [ ] Videos are successfully uploaded to Facebook Pages automatically when the setting is enabled.
- [ ] Vertical videos with appropriate duration are correctly identified and uploaded as Reels.
- [ ] Metadata (Title/Description) matches the YouTube metadata for the same video.
- [ ] No existing YouTube or generation logic is modified in a breaking way; the Facebook integration acts as an optional post-processing step.

## Out of Scope
- Interactive OAuth flow in the UI for obtaining tokens.
- Deleting videos from Facebook via the app.
- Fetching comments or engagement metrics from Facebook.

## Manual Actions (Meta for Developers)
To enable this feature, the user must perform the following on the Meta for Developers portal:
1. Create a Meta App (Type: Business).
2. Add the "Facebook Login" and "Page Public Content Access" products.
3. Obtain a Page Access Token with `pages_manage_posts`, `pages_read_engagement`, and `publish_video` permissions.
4. Convert the short-lived token to a long-lived token (10 years/permanent).
5. Retrieve the Facebook Page ID.
