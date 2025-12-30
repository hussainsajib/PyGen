# Implementation Plan: Multi-Language Metadata Synchronization

## Phase 1: Database & Model Expansion
- [x] Task: Expand Language model and migrate
    - [x] Sub-task: Add `brand_name` column to `Language` model in `db/models/language.py`.
    - [x] Sub-task: Create a migration script to add the column and update existing rows ('bengali' -> 'তাকওয়া বাংলা', 'english' -> 'Taqwa').
- [x] Task: Implement Surah model and seeding
    - [x] Sub-task: Define `Surah` model in `db/models/surah.py` with localized name columns.
    - [x] Sub-task: Create a seeding script to populate the `surahs` table from `data/surah_data.json`.
- [~] Task: Conductor - User Manual Verification 'Phase 1: Database & Model Expansion' (Protocol in workflow.md)

## Phase 2: Video Overlay Localization
- [ ] Task: Refactor brand rendering
    - [ ] Sub-task: Update `factories/single_clip.py` to remove hardcoded brand strings from `generate_brand_clip`.
    - [ ] Sub-task: Update `processes/surah_video.py` to fetch the localized `brand_name` from the `Language` table.
- [ ] Task: Localize Surah and Reciter rendering
    - [ ] Sub-task: Update `processes/surah_video.py` to fetch Surah metadata from the new `surahs` table instead of JSON.
    - [ ] Sub-task: Ensure `Reciter` names are fetched from the DB based on the active language.
    - [ ] Sub-task: Update `generate_reciter_name_clip` and `generate_surah_info_clip` to use the localized strings.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Video Overlay Localization' (Protocol in workflow.md)

## Phase 3: Information File Localization
- [ ] Task: Localize generated text files
    - [ ] Sub-task: Refactor `processes/description.py` to use language-specific labels (e.g., "Reciter" vs "ক্বারী").
    - [ ] Sub-task: Ensure the file content (names of Surahs/Reciters) uses the database-stored localized strings.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Information File Localization' (Protocol in workflow.md)

## Phase 4: Integration & Final Verification
- [ ] Task: End-to-End Verification
    - [ ] Sub-task: Verify a full Bengali video generation (brand, names, .txt file).
    - [ ] Sub-task: Verify a full English video generation (brand, names, .txt file).
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Integration & Final Verification' (Protocol in workflow.md)
