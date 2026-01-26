# Plan: Mushaf Video Generation Feature

This plan outlines the implementation of a new video generation engine that renders Mushaf-style layouts with active line highlighting and integrated background selection.

## Phase 1: Data Alignment & Core Rendering [checkpoint: 70de69a]
- [x] Task: Implement a utility to map WBW timestamps to Mushaf lines. 50f892e
    - [x] Write unit tests for timestamp alignment (ensuring correct start/end times per line).
    - [x] Implement `get_mushaf_line_timestamps` in `db_ops/crud_mushaf.py`.
- [x] Task: Create the core Mushaf clip generator using MoviePy. 245de8d
    - [x] Write unit tests for the clip generator (mocking MoviePy components).
    - [x] Implement `generate_mushaf_page_clip` in `factories/single_clip.py` or a new factory.
    - [x] Add logic for semi-transparent line highlighting/glow based on active timestamps.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Data Alignment & Core Rendering' (Protocol in workflow.md) 1c7e586

## Phase 2: Process Orchestration & API [checkpoint: 17dc452]
- [x] Task: Implement the Mushaf video generation process. 1c7e586
    - [x] Create `create_mushaf_video_job` in `processes/processes.py`.
    - [x] Integrate Header (Bismillah), Footer (Metadata), and Progress Bar overlays.
- [x] Task: Create the web endpoint for job submission. 1c7e586
    - [x] Write integration tests for the `/create-mushaf-video` route.
    - [x] Implement the route in `app.py`.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Process Orchestration & API' (Protocol in workflow.md) 17dc452

## Phase 3: Frontend Interface Integration [checkpoint: 06300c0]
- [x] Task: Implement the Mushaf Video Creator page. 01e3051
    - [x] Create `templates/mushaf_video.html` extending `base.html`.
    - [x] Add Surah and Reciter selection dropdowns.
    - [x] Add a configuration input for "Visible Lines per Scene".
- [x] Task: Integrate the Background Selection Module. 01e3051
    - [x] Extract the background selector from `wbw.html` into a reusable snippet or include it.
    - [x] Ensure Unsplash/Pexels/Upload functionality works within the new page.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Frontend Interface' (Protocol in workflow.md) fd0873d

## Phase 4: Final Integration & Verification
- [ ] Task: Perform end-to-end manual verification.
    - [ ] Generate a 15-line Mushaf video and verify sync/highlighting.
    - [ ] Generate a 5-line Mushaf video and verify paging/scrolling behavior.
    - [ ] Confirm all overlays (Header, Footer, Progress) render correctly.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Integration & Verification' (Protocol in workflow.md)
