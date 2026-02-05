# Implementation Plan: Juz-Based Mushaf Video Generation

This plan outlines the steps to implement Juz-level video generation, including database access, audio processing with timestamp mapping, and a dedicated user interface.

## Phase 1: Data Access and Logic Layer [checkpoint: 334e017]
- [x] Task: Implement Juz metadata service to retrieve boundaries from SQLite. [aa97f19]
    - [ ] Write unit tests for `get_juz_boundaries` in `tests/test_juz_metadata.py`.
    - [ ] Implement query logic in `db_ops/crud_mushaf.py` to fetch start/end Surah/Ayah for a Juz.
- [x] Task: Develop the Audio/Timing mapping engine. [e908ae3]
    - [ ] Write unit tests for timing offsets (including Basmallah and Surah 9 gaps) in `tests/test_juz_timing.py`.
    - [ ] Implement `prepare_juz_data_package` to concatenate audio streams and re-map word-level timestamps relative to the Juz start.
- [ ] Task: Conductor - User Manual Verification 'Data Access and Logic Layer' (Protocol in workflow.md)

## Phase 2: Video Generation Engine Enhancements [checkpoint: b518cdd]
- [x] Task: Implement multi-Surah Mushaf chunking logic. [8988c01]
    - [ ] Write integration tests for the continuous 15-line flow across Surah boundaries.
    - [ ] Modify or create a variant of `generate_mushaf_video` that iterates through a list of Surahs while maintaining line state.
- [x] Task: Implement Surah transition injection. [e79da71]
    - [ ] Write tests to verify Surah header and Basmallah injection at specific transition Ayahs.
    - [ ] Update the line assembly logic to inject headers and ligatures between Surahs.
- [ ] Task: Conductor - User Manual Verification 'Video Generation Engine Enhancements' (Protocol in workflow.md)

## Phase 3: Metadata and Integration
- [ ] Task: Implement automated chapter marker generation.
    - [ ] Write tests for description generation with timestamped Surah names.
    - [ ] Update `processes/description.py` to handle Juz-specific templates and chapter lists.
- [ ] Task: Conductor - User Manual Verification 'Metadata and Integration' (Protocol in workflow.md)

## Phase 4: Frontend Development
- [ ] Task: Create the Juz Video generation interface.
    - [ ] Develop `templates/juz_video.html` using Bootstrap 5, mirroring the Mushaf creation layout.
    - [ ] Implement Juz selection (1-30) and integrate the existing background/opacity modules.
- [ ] Task: Wire the UI to the backend job system.
    - [ ] Add the `/juz-video` route to `app.py`.
    - [ ] Create the `create_juz_video_job` function in `processes/processes.py`.
- [ ] Task: Conductor - User Manual Verification 'Frontend Development' (Protocol in workflow.md)
