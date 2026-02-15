# Specification: Automated Basmallah Injection for Mushaf Videos

## Overview
This feature introduces automated injection of a standardized Basmallah audio file (`recitation_data/basmalah.mp3`) at the beginning of Mushaf videos. This ensures a consistent and high-quality opening for Surah recitations within both standalone Surah videos and continuous Juz-level videos, while respecting traditional exceptions (Surah 1 and Surah 9). A configurable silence duration is added to provide a natural transition.

## Functional Requirements
1.  **Audio Injection:**
    -   Automatically prepend `recitation_data/basmalah.mp3` to the audio stream for Surah and Juz videos.
    -   **Exceptions:** Do NOT inject the file for Surah 1 (Al-Fatiha) and Surah 9 (At-Tawbah). For these surahs, the system must rely strictly on the database records and the reciter's provided audio.
2.  **Visual Synchronization:**
    -   While the injected Basmallah audio is playing, the Mushaf scene containing the "Bismillah" line (`line_type: basmallah`) must be displayed.
    -   The "Bismillah" line should be displayed **statically** (no highlighting) for the duration of the injected audio.
3.  **Transition Logic:**
    -   Inject a configurable period of silence between the end of the `basmalah.mp3` and the start of the first Ayah's recitation.
    -   **Configuration:** The duration is controlled by a new setting `MUSHAF_BASMALLAH_SILENCE_DURATION` (default: 1.0 seconds).
4.  **UI & Management:**
    -   Add `MUSHAF_BASMALLAH_SILENCE_DURATION` to the configuration dashboard to allow users to adjust the duration in real-time.
    -   Persist the setting in the PostgreSQL database.
5.  **Scope:**
    -   Applies to `generate_mushaf_video` in `processes/mushaf_video.py`.
    -   Applies to `generate_juz_video` in `processes/mushaf_video.py`.
6.  **Data Integration:**
    -   Coordinate with `prepare_juz_data_package` to ensure the continuous Juz audio stream incorporates the injected Basmallah at appropriate Surah transitions.

## Non-Functional Requirements
-   **Performance:** The audio concatenation and silence injection should not significantly increase video generation time.
-   **Maintainability:** The injection logic should be modularized to allow for future adjustments.

## Acceptance Criteria
-   [ ] Standalone Mushaf videos for Surahs (except 1 and 9) start with the `basmalah.mp3` audio.
-   [ ] Juz-level videos correctly inject the Basmallah at the start of each Surah (except 1 and 9).
-   [ ] The "Bismillah" line in the Mushaf layout is visible during the injected audio but remains unhighlighted.
-   [ ] The silence duration between the Basmallah and the first Ayah matches the `MUSHAF_BASMALLAH_SILENCE_DURATION` setting.
-   [ ] The setting is adjustable via the UI and persists in the database.
-   [ ] Surah 1 and Surah 9 videos do not have the `basmalah.mp3` injected.

## Out of Scope
-   Automated Basmallah injection for Word-by-Word (non-Mushaf) videos.
-   Dynamic selection of different Basmallah audio files.
