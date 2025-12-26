# Track Specification: Manual Video Upload Dashboard

## Overview
This track introduces a new management interface within PyGen to handle the manual upload of existing, generated Islamic videos to YouTube. It aims to bridge the gap for videos that were generated without the automatic upload flag enabled or failed during initial processing.

## Functional Requirements
- **Dashboard Endpoint:** A new web route (e.g., `/manual-upload`) to list all generated videos.
- **Asset Discovery:** Scan `exported_data/videos`, `exported_data/screenshots`, and `exported_data/details` to identify available assets.
- **File Matching:**
    - Videos: `quran_video_{surah_number}_{reciter}.mp4`
    - Screenshots: `screenshot_quran_video_{surah_number}_{reciter}.png`
    - Details: `{surah_number}_{start_ayah}_{end_ayah}_{reciter}.txt`
- **Dashboard Display:**
    - Show video filename and reciter name.
    - Status indicators for "Details Present" and "Screenshot Present".
    - YouTube Playlist status: Indicate if the reciter has an existing playlist.
- **Manual Upload Trigger:** A button for each video to initiate the upload to the reciter's specific YouTube playlist.

## Non-Functional Requirements
- **Asynchronous Processing:** Uploads should be handled in the background to avoid blocking the UI.
- **UI Consistency:** Follow the "Modern and Bold" theme established in the product guidelines.

## Acceptance Criteria
- [ ] New endpoint `/manual-upload` is accessible.
- [ ] All existing videos in `exported_data/videos` are listed with correct reciter mapping.
- [ ] The presence of screenshots and detail files is accurately reflected for each video.
- [ ] "Upload to YouTube" button triggers a background job.
- [ ] Video is successfully uploaded to the correct reciter playlist on YouTube with metadata from the details file.

## Out of Scope
- Re-generating videos or assets (this track focuses on existing files).
- Multi-video bulk selection (initial implementation focuses on individual manual triggers).
