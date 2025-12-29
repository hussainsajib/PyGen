# Track Specification: Multi-Language Support

## Overview
This track introduces multi-language support to the PyGen platform, enabling video generation in both Bengali and English. It involves database schema updates, configuration management, file system reorganization for translation assets, and code refactoring to support language-specific operations.

## Functional Requirements
- **Language Management:**
    - A new database table `languages` must exist with initial values: 'bengali' and 'english'.
    - Users must be able to set a `DEFAULT_LANGUAGE` via the Configuration UI.
- **UI Updates:**
    - The `/config` page must feature a dropdown menu populated from the `languages` table to select the default language.
- **Asset Organization:**
    - The `databases/translation` directory must be restructured.
    - Existing files move to `databases/translation/bengali`.
    - A new directory `databases/translation/english` must be created.
- **Video Generation:**
    - The system must select the correct translation database based on the configured default language (or a job-specific override if implemented).

## Technical Requirements
- **Database:**
    - Create a `Language` model (SQLAlchemy).
    - Seed the table on startup or migration.
    - Add `DEFAULT_LANGUAGE` key to the `config` table.
- **File System:**
    - Move `databases/translation/*.db` (or `*.json`/`*.txt` depending on actual content) to `databases/translation/bengali/`.
    - Ensure `databases/translation/english/` exists.
- **Code Refactoring:**
    - Update `db_ops/crud_translation.py` (or equivalent) to construct paths dynamically: `databases/translation/{language}/{filename}`.
    - Update `config_manager.py` to handle the new setting.

## Acceptance Criteria
- [ ] `languages` table exists and contains 'bengali' and 'english'.
- [ ] Config UI shows a dropdown for 'Default Language' and saves the selection correctly.
- [ ] Existing translation files are moved to `databases/translation/bengali`.
- [ ] Video generation works correctly using the Bengali translation when 'bengali' is selected.
- [ ] The system handles the new directory structure without errors.
