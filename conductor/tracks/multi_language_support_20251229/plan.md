# Implementation Plan: Multi-Language Support

## Phase 1: Database & Configuration Infrastructure
- [x] Task: Create Language model and seed data
    - [x] Sub-task: Define `Language` model in `db/models/language.py` (or similar).
    - [x] Sub-task: Create a migration/init script to create the table and insert 'bengali', 'english'.
- [x] Task: Add configuration setting
    - [x] Sub-task: Update `config_manager.py` or migration script to add `DEFAULT_LANGUAGE` (default: 'bengali').
    - [x] Sub-task: Update `db_ops` to fetch available languages.
- [x] Task: Update Configuration UI
    - [x] Sub-task: Modify `templates/config.html` to include a dropdown for language selection.
    - [x] Sub-task: Update `app.py` (config route) to pass language options to the template.
- [~] Task: Conductor - User Manual Verification 'Phase 1: Database & Configuration Infrastructure' (Protocol in workflow.md)

## Phase 2: Asset Reorganization & Code Refactoring
- [ ] Task: Reorganize translation database files
    - [ ] Sub-task: Create `databases/translation/bengali` and `databases/translation/english`.
    - [ ] Sub-task: Move existing translation files to the `bengali` folder.
- [ ] Task: Refactor translation access logic
    - [ ] Sub-task: Identify where translation files are loaded (likely `db_ops` or `processes`).
    - [ ] Sub-task: Update logic to use `DEFAULT_LANGUAGE` config to resolve the path (e.g., `databases/translation/{lang}/...`).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Asset Reorganization & Code Refactoring' (Protocol in workflow.md)

## Phase 3: Integration & Verification
- [ ] Task: Verify End-to-End Video Generation
    - [ ] Sub-task: Ensure that the video generation process picks up the correct translation file based on the config.
    - [ ] Sub-task: Add a test case to verify path resolution for both languages.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Integration & Verification' (Protocol in workflow.md)
