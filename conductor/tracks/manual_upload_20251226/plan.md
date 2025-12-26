# Implementation Plan: Manual Video Upload Dashboard

## Phase 1: Foundation and UI
- [ ] Task: Create initial route and template for the manual upload dashboard
    - [ ] Sub-task: Write failing test for the `/manual-upload` route
    - [ ] Sub-task: Implement the FastAPI route and a basic Jinja2 template
- [ ] Task: Implement asset discovery logic
    - [ ] Sub-task: Write failing test for scanning `exported_data` directories
    - [ ] Sub-task: Implement logic to list videos and match with screenshots/details
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundation and UI' (Protocol in workflow.md)

## Phase 2: Reciter and Playlist Integration
- [ ] Task: Map videos to Reciter database entities
    - [ ] Sub-task: Write failing test for reciter mapping from filenames
    - [ ] Sub-task: Implement reciter identification and metadata retrieval
- [ ] Task: Verify YouTube playlist availability for reciters
    - [ ] Sub-task: Write failing test for checking playlists via YouTube API
    - [ ] Sub-task: Implement playlist check and display status in UI
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Reciter and Playlist Integration' (Protocol in workflow.md)

## Phase 3: Background Upload Integration
- [ ] Task: Create background upload job
    - [ ] Sub-task: Write failing test for triggering an upload job
    - [ ] Sub-task: Implement the background task logic using existing YouTube utilities
- [ ] Task: Add "Upload" button and progress feedback
    - [ ] Sub-task: Write failing test for the upload button interaction
    - [ ] Sub-task: Update UI with upload trigger and real-time status updates
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Background Upload Integration' (Protocol in workflow.md)
