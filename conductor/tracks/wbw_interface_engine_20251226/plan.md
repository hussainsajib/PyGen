# Implementation Plan: Word-by-Word Video Creation Interface and Engine

## Phase 1: Backend Infrastructure and UI [checkpoint: e7f8ab1]
- [x] Task: Create Word-by-Word endpoint and template
    - [x] Sub-task: Write failing test for the `/word-by-word` route
    - [x] Sub-task: Implement the FastAPI route in `app.py` with filtered reciter logic
    - [x] Sub-task: Create `templates/wbw.html` mirroring `index.html` with modified defaults
- [x] Task: Add navigation link to navbar
    - [x] Sub-task: Update `templates/base.html` to include the "Word-by-Word" link
- [x] Task: Conductor - User Manual Verification 'Phase 1: Backend Infrastructure and UI' (Protocol in workflow.md)

## Phase 2: WBW Timestamp Retrieval Logic
- [ ] Task: Implement WBW Database utility
    - [ ] Sub-task: Write failing test for fetching word-level timestamps from a mock SQLite database
    - [ ] Sub-task: Create a utility function in `db_ops/crud_wbw.py` to fetch timestamps for a given surah and ayah range
- [ ] Task: Conductor - User Manual Verification 'Phase 2: WBW Timestamp Retrieval Logic' (Protocol in workflow.md)

## Phase 3: Video Engine Modifications
- [ ] Task: Implement WBW clip generation
    - [ ] Sub-task: Write failing test for a single WBW ayah clip creation
    - [ ] Sub-task: Create `create_wbw_ayah_clip` in `processes/surah_video.py` to handle word-by-word rendering
    - [ ] Sub-task: Implement word highlighting/animation logic in `factories/single_clip.py`
- [ ] Task: Integrate WBW logic into generation workflow
    - [ ] Sub-task: Update `generate_surah` or create a WBW-specific version to use the new clip creation logic
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Video Engine Modifications' (Protocol in workflow.md)
