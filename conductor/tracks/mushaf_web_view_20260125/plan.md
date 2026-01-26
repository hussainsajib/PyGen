# Plan: Mushaf Web View Feature

This plan outlines the steps to implement a traditional 15-line Mushaf layout on the PyGen web platform, including dynamic font loading and page navigation.

## Phase 1: Backend Data & API [checkpoint: 3c25132]
- [x] Task: Implement a service to retrieve Mushaf page data. 49cd7d3
    - [x] Write unit tests for the page data service (mocking both SQLite databases).
    - [x] Implement the logic to fetch line boundaries and map words for a given page number.
- [x] Task: Implement the web routes and static font serving. 453054e
    - [x] Write integration tests for the `/mushaf` route and the font serving endpoint.
    - [x] Create the `/mushaf` endpoint in `app.py`.
    - [x] Configure FastAPI to serve the `QPC_V2_Font.ttf` directory as static assets.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Backend Data & API' (Protocol in workflow.md) 3c25132

## Phase 2: Frontend Template & Dynamic Fonts
- [x] Task: Create the Mushaf base template. c5663a0
    - [x] Create `templates/mushaf.html` with the 15-line container structure.
    - [x] Implement CSS for the "Mushaf aesthetic" (cream background, specific line heights, centered text).
- [x] Task: Implement dynamic font loading. c5663a0
    - [x] Add a JavaScript/Jinja2 mechanism to inject the correct `@font-face` declaration for the current page.
    - [x] Ensure words are rendered using the `PageFont` family.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Frontend Template & Dynamic Fonts' (Protocol in workflow.md)
    - [ ] Add a JavaScript/Jinja2 mechanism to inject the correct `@font-face` declaration for the current page.
    - [ ] Ensure words are rendered using the `PageFont` family.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Frontend Template & Dynamic Fonts' (Protocol in workflow.md)

## Phase 3: Navigation & Interactive Controls
- [ ] Task: Add navigation components to the UI.
    - [ ] Implement a page selector (dropdown or slider) for 1-604.
    - [ ] Add "Previous" and "Next" navigation buttons.
- [ ] Task: Implement interactive page switching.
    - [ ] Add JavaScript logic to handle page updates (either via URL redirects or AJAX).
    - [ ] Ensure the UI remains responsive and the correct font loads on every page change.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Navigation & Controls' (Protocol in workflow.md)
