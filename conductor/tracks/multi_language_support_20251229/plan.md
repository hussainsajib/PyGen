# Implementation Plan: Multi-Language Support

## Phase 1: Database & Configuration Infrastructure [checkpoint: 9b2191f]
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

## Phase 2: Asset Reorganization & Code Refactoring [checkpoint: db074c6]
- [x] Task: Reorganize translation database files
    - [x] Sub-task: Create `databases/translation/bengali` and `databases/translation/english`.
    - [x] Sub-task: Move existing translation files to the `bengali` folder.
- [x] Task: Refactor translation access logic
    - [x] Sub-task: Identify where translation files are loaded (likely `db_ops` or `processes`).
    - [x] Sub-task: Update logic to use `DEFAULT_LANGUAGE` config to resolve the path (e.g., `databases/translation/{lang}/...`).
- [~] Task: Conductor - User Manual Verification 'Phase 2: Asset Reorganization & Code Refactoring' (Protocol in workflow.md)

## Phase 3: Integration & Verification [checkpoint: 32a322c]
- [x] Task: Verify End-to-End Video Generation
    - [x] Sub-task: Ensure that the video generation process picks up the correct translation file based on the config.
    - [x] Sub-task: Add a test case to verify path resolution for both languages.
- [x] Task: Implement Per-Language Font Support
    - [x] Sub-task: Add `font` column to `Language` model.
    - [x] Sub-task: Update `scripts/init_languages.py` to seed default fonts.
    - [x] Sub-task: Update `processes/surah_video.py` to fetch and use the font for the current language.
    - [x] Sub-task: Update Config UI to allow editing fonts for languages (or just seeding is enough for now?).
- [x] Task: Conductor - User Manual Verification 'Phase 3: Integration & Verification' (Protocol in workflow.md)
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Integration & Verification' (Protocol in workflow.md)
