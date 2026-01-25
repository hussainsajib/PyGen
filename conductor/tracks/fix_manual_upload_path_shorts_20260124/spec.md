# Specification: Fix Manual Upload Path for Shorts

## Overview
The "Manual Upload" feature fails to upload YouTube Shorts because it incorrectly attempts to locate the video files in `exported_data/videos/` instead of `exported_data/shorts/`. This results in a `FileNotFoundError` (Errno 2) when triggering an upload for a Short.

## Functional Requirements
- **Correct Path Resolution:** The system must accurately determine the file path for a video based on whether it is categorized as a "Short" or a standard video.
- **Dynamic Directory Selection:** 
    - Standard videos should continue to be sourced from `exported_data/videos/`.
    - Shorts (identifiable by their filename prefix `quran_shorts_` or an `is_short` flag in the metadata) must be sourced from `exported_data/shorts/`.
- **Validation:** Ensure that the YouTube upload process (specifically the `manual_upload` route or associated utility) uses this corrected path.

## Non-Functional Requirements
- **Robustness:** The system should handle cases where a file might be missing from both locations gracefully (though the primary goal is fixing the path).

## Acceptance Criteria
- [ ] Attempting to upload a Short from the "Manual Upload" dashboard no longer results in a `FileNotFoundError`.
- [ ] The system correctly identifies and uploads files from `exported_data/shorts/` when they are Shorts.
- [ ] standard videos in `exported_data/videos/` still upload correctly.

## Out of Scope
- Migrating existing files between directories.
- Refactoring the entire file storage system.
