# Implementation Plan: Reciter WBW Database Field

## Phase 1: Model and Schema Migration [checkpoint: b965923]
- [x] Task: Update Reciter Model
    - [x] Sub-task: Write failing test for `wbw_database` field in the model
    - [x] Sub-task: Add `wbw_database` column to `Reciter` model in `db/models/reciter.py`
- [x] Task: Database Schema Migration
    - [x] Sub-task: Execute SQL command to add `wbw_database` column to the `reciters` table in PostgreSQL
- [x] Task: Conductor - User Manual Verification 'Phase 1: Model and Schema Migration' (Protocol in workflow.md)

## Phase 2: CRUD and Validation Logic [checkpoint: 86cd72b]
- [x] Task: Update Reciter CRUD Operations
    - [x] Sub-task: Write failing tests for CRUD operations including the `wbw_database` field
    - [x] Sub-task: Update create and update functions in `db_ops/crud_reciters.py`
- [x] Task: Implement WBW File Validation
    - [x] Sub-task: Write failing test for the `databases/word-by-word` file existence check
    - [x] Sub-task: Implement a validation utility to check if the file exists on disk
- [x] Task: Conductor - User Manual Verification 'Phase 2: CRUD and Validation Logic' (Protocol in workflow.md)

## Phase 3: UI and Form Integration [checkpoint: b0a3107]
- [x] Task: Update Reciter Forms
    - [x] Sub-task: Modify `templates/reciter_form.html` to include the "WBW Database" text input field
- [x] Task: Update FastAPI Routes
    - [x] Sub-task: Write failing test for form submission with WBW validation (success and failure cases)
    - [x] Sub-task: Update `reciter_create` and `reciter_update` routes in `app.py` to handle the new field and display validation errors
- [x] Task: Conductor - User Manual Verification 'Phase 3: UI and Form Integration' (Protocol in workflow.md)
