# Implementation Plan: Enhanced YouTube Metadata and SEO for Shorts

## Phase 1: Database and UI Infrastructure [checkpoint: c99b0b5]
- [x] Task: Update Job model and Database Schema
    - [x] Sub-task: Add `custom_title` column to the `Job` model in `db/models/job.py`.
    - [x] Sub-task: Create and run a migration script to add the `custom_title` column to the `jobs` table in PostgreSQL.
- [x] Task: Update Frontend Interfaces
    - [x] Sub-task: Add a "Video Title" text input to `templates/index.html` and `templates/wbw.html`.
    - [x] Sub-task: Implement JavaScript logic in both templates to show/hide the "Video Title" field only when "Short" is selected.
- [x] Task: Update Web Routes
    - [x] Sub-task: Modify the `/create-video` and `/create-surah-video` routes in `app.py` to capture and store the `custom_title` when enqueuing jobs.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Database and UI Infrastructure' [c99b0b5] (Protocol in workflow.md)

## Phase 2: Metadata and SEO Logic implementation
- [x] Task: Implement SEO-optimized description and tag generation
    - [x] Sub-task: Write failing tests for the new metadata generation logic (Title, Description, and 10-15 Tags).
    - [x] Sub-task: Update `processes/description.py` to include a helper function that generates Shorts-specific metadata, including dynamic CTAs, social links, and Surah-based keywords.
- [x] Task: Refine Video Details Export
    - [x] Sub-task: Update `generate_details` to include the optimized Shorts metadata in the exported `.txt` files.
- [~] Task: Conductor - User Manual Verification 'Phase 2: Metadata and SEO Logic implementation' (Protocol in workflow.md)

## Phase 3: YouTube Upload Integration [checkpoint: e959396]
- [x] Task: Update YouTube Upload logic
    - [x] Sub-task: Write failing tests for `upload_to_youtube` to ensure it correctly applies optimized metadata for Shorts while leaving regular videos untouched.
    - [x] Sub-task: Modify `processes/youtube_utils.py` to incorporate the enhanced title, description, and dynamic tags during the initialization of the upload request.
- [x] Task: Propagate Title through Job Worker
    - [x] Sub-task: Update `processes/processes.py` and the job worker to ensure the `custom_title` is passed correctly to the generation and upload functions.
- [x] Task: Conductor - User Manual Verification 'Phase 3: YouTube Upload Integration' [e959396] (Protocol in workflow.md)

## Phase 4: Final Integration and Verification
- [ ] Task: End-to-end verification
    - [ ] Sub-task: Generate a Short WBW video with a custom title and verify that the resulting YouTube metadata includes the optimized SEO tags, CTAs, and formatted title.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Integration and Verification' (Protocol in workflow.md)
