# Implementation Plan: Automated Basmallah Injection for Mushaf Videos

## Phase 1: Core Audio Utilities & Shared Logic [checkpoint: d78c610]
Implement the foundational utilities for managing the standardized Basmallah audio and silence injection.

- [x] Task: Write unit tests for Basmallah audio validation and silence generation in `tests/test_audio_utils.py`. 81db9e1
- [x] Task: Implement `get_standard_basmallah_clip` and `generate_transition_silence` in a new utility or existing `factories/video.py`. 32eee76
- [x] Task: Update `processes/mushaf_video.py` to import these new utilities. e7f82da
- [x] Task: Conductor - User Manual Verification 'Core Audio Utilities & Shared Logic' (Protocol in workflow.md) e7f82da

## Phase 2: Configuration & UI Integration [checkpoint: a144d9d]
Implement the database persistence and UI management for the Basmallah silence duration.

- [x] Task: Add `MUSHAF_BASMALLAH_SILENCE_DURATION` to the database initialization/seeds. 8913398
- [x] Task: Update the configuration dashboard template (`templates/config.html`) to include the new silence duration setting. 76dca4e
- [x] Task: Update the configuration save/load logic in `app.py` or the relevant controller to handle this setting. e802847
- [x] Task: Conductor - User Manual Verification 'Configuration & UI Integration' (Protocol in workflow.md) e802847

## Phase 3: Standalone Mushaf Video Integration [checkpoint: 24168b2]
Update the standard Surah video generation workflow to incorporate the automated injection.

- [x] Task: Write integration tests for `generate_mushaf_video` with Basmallah injection in `tests/test_mushaf_injection.py`. d4fc19f
- [x] Task: Refactor `generate_mushaf_video` to inject `basmalah.mp3` and dynamic silence at the start of the audio stream. d4fc19f
- [x] Task: Implement exception logic to skip injection for Surah 1 and Surah 9. d4fc19f
- [x] Task: Adjust the rendering loop to display the Mushaf's "Bismillah" line statically during the injected audio. d4fc19f
- [x] Task: Conductor - User Manual Verification 'Standalone Mushaf Video Integration' (Protocol in workflow.md) d4fc19f

## Phase 4: Juz Mushaf Video Integration [checkpoint: 24168b2]
Extend the Juz generation workflow to handle sequential Basmallah injection at Surah transitions.

- [x] Task: Write integration tests for `generate_juz_video` with multi-surah injection in `tests/test_juz_injection.py`. d4fc19f
- [x] Task: Update `prepare_juz_data_package` in `processes/mushaf_video.py` to inject Basmallah and dynamic silence at each valid Surah transition. d4fc19f
- [x] Task: Recalculate word-level timestamp offsets to account for the additional injected durations. d4fc19f
- [x] Task: Ensure the visual paging logic correctly identifies and displays the Bismillah line during transition periods. d4fc19f
- [x] Task: Conductor - User Manual Verification 'Juz Mushaf Video Integration' (Protocol in workflow.md) d4fc19f

## Phase 5: Finalization & Documentation
Wrap up the track with final checks and documentation.

- [x] Task: Verify overall system performance and memory usage during bulk generation. 24168b2
- [~] Task: Update project documentation if any configuration constants were introduced.
- [ ] Task: Conductor - User Manual Verification 'Finalization & Documentation' (Protocol in workflow.md)
