# Track Specification: Multi-Language Metadata Synchronization

## Overview
This track ensures that when the system's `DEFAULT_LANGUAGE` is changed, all metadata rendered in the video (Surah name, Reciter name, Brand name) and the generated information text file are automatically localized to that language.

## Functional Requirements
- **Brand Localization:**
    - The `languages` table will be updated to include a `brand_name` column.
    - Videos will display the brand name associated with the selected language (e.g., "তাকওয়া বাংলা" for Bengali, "Taqwa" for English).
- **Localized Entities (Surah & Reciter):**
    - A new `surahs` table will be created in the database to store Surah metadata (localized names, verse counts, etc.).
    - The existing `reciters` table and new `surahs` table will use column-based localization (`english_name` and `bangla_name`).
    - Video overlays (intro, footer, etc.) must use the name corresponding to the selected language.
- **Information File Localization:**
    - The `.txt` file generated for each video (containing details about the recitation) must be fully localized (labels and values) based on the language setting.

## Technical Requirements
- **Database Schema:**
    - Migration: Add `brand_name` column to `languages` table.
    - New Model: `Surah` model with `number`, `english_name`, `bangla_name`, `total_verses`, etc.
    - Seeding: Seed the `surahs` table from `data/surah_data.json`.
- **Refactoring:**
    - Update `processes/surah_video.py` and `factories/single_clip.py` to fetch localized brand, surah, and reciter names from the database instead of hardcoded strings or JSON files.
    - Update `processes/description.py` (or wherever info files are generated) to support template-based or logic-based localization.

## Acceptance Criteria
- [ ] When `DEFAULT_LANGUAGE` is 'english', video overlays show English names and "Taqwa".
- [ ] When `DEFAULT_LANGUAGE` is 'bengali', video overlays show Bengali names and "তাকওয়া বাংলা".
- [ ] The generated info text file switches content language based on the configuration.
- [ ] Surah metadata is successfully migrated to and sourced from the database.

## Out of Scope
- Adding support for languages other than Bengali and English in this track.
- Localizing the web interface (templates) itself (only video/file outputs).
