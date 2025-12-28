# Implementation Plan: Paginated Background Selection

## Phase 1: Backend API Enhancements
- [x] Task: Update Unsplash search to support pagination
    - [x] Sub-task: Modify `search_unsplash` in `net_ops/unsplash.py` to accept `page` and `per_page` parameters and pass them to the Unsplash API request.
    - [x] Sub-task: Update the `/unsplash-search` route in `app.py` to handle the new `page` query parameter and pass it to the search function.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Backend API Enhancements' (Protocol in workflow.md)

## Phase 2: Frontend UI Implementation
- [x] Task: Implement pagination controls in background modal
    - [x] Sub-task: Update `templates/index.html` and `templates/wbw.html` to add "Previous" and "Next" buttons and a page indicator within the modal.
    - [x] Sub-task: Refactor the `searchUnsplash` JavaScript function to maintain `currentPage` state and handle pagination logic.
    - [x] Sub-task: Implement `changePage` logic to increment/decrement `currentPage`, re-fetch images, and scroll the modal to the top.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Frontend UI Implementation' (Protocol in workflow.md)

## Phase 3: Final Integration and UI Refinement
- [x] Task: Verify cross-interface consistency
    - [x] Sub-task: Ensure the paginated search works correctly on both the home page and the word-by-word page.
    - [x] Sub-task: Finalize button visibility logic (hiding "Previous" on Page 1).
- [x] Task: Conductor - User Manual Verification 'Phase 3: Final Integration and UI Refinement' [checkpoint: 87cefb4] (Protocol in workflow.md)
