# Specification: Duration Validation for YouTube Shorts

## Overview
YouTube Shorts have a strict 60-second duration limit. Currently, the system attempts to upload any video categorized as a "Short" regardless of its length. This track implements a post-generation validation step to ensure that if a generated "Word-by-Word" Short exceeds 60 seconds, it is not uploaded to YouTube, while still allowing the Facebook upload to proceed.

## Functional Requirements

### 1. Post-Generation Duration Check
- Immediately after a video is generated, the system must retrieve the actual duration of the resulting file (e.g., using `moviepy` or `ffprobe`).
- This check applies specifically to jobs where `is_short` is `True`.

### 2. YouTube Upload Logic
- If the duration is **<= 60 seconds**, the YouTube upload proceeds as normal.
- If the duration is **> 60 seconds**, the YouTube upload must be skipped.
- An informative warning message must be logged (e.g., "YouTube upload skipped: Short exceeds 60 seconds").
- The job's internal status for YouTube should reflect this skip/warning, though the overall job may still reach "completed" if other tasks succeed.

### 3. Facebook Upload Logic
- The Facebook upload should proceed regardless of the video duration, as per current requirements ("it's fine for now").

### 4. Job Status & Reporting
- If a YouTube upload is skipped due to duration, the overall job should be considered a "Partial Success".
- The UI should ideally reflect that the YouTube upload was skipped for this specific reason.

## Non-Functional Requirements
- **Accuracy:** The duration measurement must be precise to avoid false positives/negatives near the 60-second mark.
- **Maintainability:** The validation logic should be centralized so it can be reused or updated if platform limits change.

## Acceptance Criteria
- [ ] Generated Short <= 60s uploads to both YouTube and Facebook.
- [ ] Generated Short > 60s skips YouTube upload but proceeds with Facebook upload.
- [ ] A clear warning is logged when a YouTube upload is skipped due to duration.
- [ ] Standard (non-Short) videos are unaffected by this 60s limit.

## Out of Scope
- Trimming videos automatically to fit the limit.
- Implementing duration checks for standard YouTube videos.
- Implementing duration checks for Facebook Reels/Videos in this track.
