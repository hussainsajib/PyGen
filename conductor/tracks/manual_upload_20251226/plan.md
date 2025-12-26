# Implementation Plan: Manual Video Upload Dashboard

## Phase 1: Foundation and UI [checkpoint: 41aa5ae]
- [x] Task: Create initial route and template for the manual upload dashboard c266378
    - [x] Sub-task: Write failing test for the `/manual-upload` route
    - [x] Sub-task: Implement the FastAPI route and a basic Jinja2 template
- [x] Task: Implement asset discovery logic 44468eb
    - [x] Sub-task: Write failing test for scanning `exported_data` directories
    - [x] Sub-task: Implement logic to list videos and match with screenshots/details
- [x] Task: Conductor - User Manual Verification 'Phase 1: Foundation and UI' (Protocol in workflow.md)

## Phase 2: Reciter and Playlist Integration
- [x] Task: Map videos to Reciter database entities d8064f5
    - [x] Sub-task: Write failing test for reciter mapping from filenames
    - [x] Sub-task: Implement reciter identification and metadata retrieval
- [x] Task: Verify YouTube playlist availability for reciters
    - [x] Sub-task: Write failing test for checking playlists via YouTube API
    - [x] Sub-task: Implement playlist check and display status in UI
- [x] Task: Conductor - User Manual Verification 'Phase 2: Reciter and Playlist Integration' (Protocol in workflow.md)

## Phase 3: Background Upload Integration
- [x] Task: Create background upload job e93fa6c
    - [x] Sub-task: Write failing test for triggering an upload job
    - [x] Sub-task: Implement the background task logic using existing YouTube utilities
- [x] Task: Add "Upload" button and progress feedback
    - [x] Sub-task: Write failing test for the upload button interaction
    - [x] Sub-task: Update UI with upload trigger and real-time status updates
- [x] Task: Conductor - User Manual Verification 'Phase 3: Background Upload Integration' (Protocol in workflow.md)
