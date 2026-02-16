# Implementation Plan - Automated Basmallah Injection for Juz Videos

## Phase 1: Core Data Preparation (Standard Engine)
Refactor the Juz data preparation layer to handle dynamic audio injection and global timing.

- [ ] Task: Update `prepare_juz_data_package` in `processes/mushaf_video.py`.
    - [ ] Move Basmallah injection logic inside the Surah loop.
    - [ ] Calculate cumulative `current_offset_ms` by adding Basmallah and Silence durations before each applicable Surah.
    - [ ] Assemble the `final_audio_clips` list with the correct sequence of [Basmallah, Silence, Recitation].
- [ ] Task: Create a unit test `tests/test_juz_basmallah_timing.py` to verify the cumulative offset calculation logic without generating actual video.
- [ ] Task: Conductor - User Manual Verification 'Core Data Preparation (Standard Engine)' (Protocol in workflow.md)

## Phase 2: High-Speed Engine Integration
Ensure the fast video engines utilize the new timing logic.

- [ ] Task: Verify `processes/mushaf_fast_video.py` (`generate_mushaf_fast`) correctly receives and applies the updated `all_wbw_timestamps` from Phase 1.
- [ ] Task: Run a dry-run generation for a small Juz segment (e.g., last two Surahs of Juz 30) using the FFmpeg engine to verify audio assembly.
- [ ] Task: Conductor - User Manual Verification 'High-Speed Engine Integration' (Protocol in workflow.md)

## Phase 3: Validation and Documentation
Final verification and synchronization.

- [ ] Task: Generate a full video for a multi-surah transition (e.g., transition from Surah 113 to 114 in Juz 30) and verify the Basmallah injection visually and audibly.
- [ ] Task: Update `conductor/product.md` to document Basmallah injection as a standard feature for Juz Mushaf videos.
- [ ] Task: Conductor - User Manual Verification 'Validation and Documentation' (Protocol in workflow.md)
