# Implementation Plan: Manual Upload Enhancements and Media Persistence

## Phase 1: Database Persistence Layer [checkpoint: dd235f6]
- [x] Task: Define the `MediaAsset` database model
    - [x] Sub-task: Write failing test for `MediaAsset` model creation and retrieval
    - [x] Sub-task: Implement `MediaAsset` model in `db/models/media_asset.py` with all required fields (paths, metadata, status)
- [x] Task: Implement CRUD operations for Media Assets
    - [x] Sub-task: Write failing tests for create, read, update, and delete operations
    - [x] Sub-task: Implement CRUD functions in `db_ops/crud_media_assets.py`
- [x] Task: Conductor - User Manual Verification 'Phase 1: Database Persistence Layer' (Protocol in workflow.md)

## Phase 2: Data Migration and logic Integration
- [ ] Task: Create and execute the one-time migration script
    - [ ] Sub-task: Write failing test for the migration logic (scanning and mapping)
    - [ ] Sub-task: Implement migration script to populate `media_assets` from current `exported_data/`
- [ ] Task: Integrate Media Asset persistence into existing workflows
    - [ ] Sub-task: Update video generation processes to record new assets in the database
    - [ ] Sub-task: Update YouTube upload processes to update status and video ID in the database
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Data Migration and logic Integration' (Protocol in workflow.md)

## Phase 3: UI Enhancements and Asset Viewers
- [ ] Task: Update Manual Upload Dashboard to use database records
    - [ ] Sub-task: Write failing test for fetching dashboard data from the database
    - [ ] Sub-task: Modify `/manual-upload` route and template to load data from `media_assets` table
- [ ] Task: Implement Collapsible Reciter Sections
    - [ ] Sub-task: Update `manual_upload.html` with Bootstrap collapsible components for each reciter group
- [ ] Task: Implement In-Browser Asset Viewers
    - [ ] Sub-task: Add modals or new-tab links for viewing videos, screenshots, and details text
- [ ] Task: Conductor - User Manual Verification 'Phase 3: UI Enhancements and Asset Viewers' (Protocol in workflow.md)

## Phase 4: Atomic and Bulk File Management
- [ ] Task: Implement Atomic Deletion
    - [ ] Sub-task: Write failing test for deleting a record and its 3 associated files from disk
    - [ ] Sub-task: Implement `/delete-media/{id}` endpoint with logic for disk cleanup and DB removal
- [ ] Task: Implement Bulk Deletion
    - [ ] Sub-task: Write failing test for bulk deletion logic
    - [ ] Sub-task: Implement endpoint to handle multiple IDs and perform atomic deletion for each
- [ ] Task: Update UI for Deletion Actions
    - [ ] Sub-task: Add individual delete buttons and checkboxes for multi-select bulk actions in the dashboard
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Atomic and Bulk File Management' (Protocol in workflow.md)
