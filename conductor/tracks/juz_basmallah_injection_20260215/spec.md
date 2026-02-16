# Specification: Automated Basmallah Injection for Juz Mushaf Videos

## Overview
This track aims to bring parity to Juz Mushaf videos by automatically injecting the Basmallah audio and a configurable silence period before applicable Surahs, matching the behavior of standalone Mushaf videos. This ensures a consistent and spiritually appropriate transition between Surahs within a continuous Juz recitation.

## Functional Requirements

### 1. Per-Surah Basmallah Injection
- **Target:** Juz Mushaf video generation (Standard and High-Speed engines).
- **Logic:** Inject Basmallah audio (`get_standard_basmallah_clip()`) before every Surah transition within the Juz.
- **Exceptions:** Automatically skip injection for:
    - Surah 1 (Al-Fatihah), as Basmallah is part of the first Ayah.
    - Surah 9 (At-Tawbah), as per traditional recitation standards.

### 2. Configurable Transition Silence
- **Action:** Add a silence gap after each injected Basmallah.
- **Duration:** Use the existing `MUSHAF_BASMALLAH_SILENCE_DURATION` configuration setting.

### 3. Global Timestamp Recalculation
- **Requirement:** Accurately map word-level timestamps across the entire Juz audio stream, accounting for multiple Basmallah injections and silences.
- **Strategy:** Calculate global offsets based on the accumulated duration of all previous segments (Recitations, Basmallahs, Silences) to ensure highlighting remains synchronized.

## Technical Requirements
- Update `processes/mushaf_video.py` (`prepare_juz_data_package`) to handle the loop-based injection and offset calculation.
- Ensure `processes/mushaf_fast_video.py` correctly consumes the updated data package.
- Maintain existing logic for Surah 9 silence gaps if applicable.

## Acceptance Criteria
- [ ] Juz videos containing multiple Surahs (e.g., Juz 30) feature a Basmallah and pause before each Surah (except 1 and 9).
- [ ] Highlighting remains perfectly synchronized with the recitation for the entire Juz.
- [ ] Transition duration is consistent with standalone Mushaf videos.
