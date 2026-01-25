# Plan: Mobile Optimization

This plan outlines the steps to make the PyGen web application responsive and mobile-friendly.

## Phase 1: Core Layout & Navigation
- [x] Task: Update `templates/base.html` to include the viewport meta tag.
- [x] Task: Refactor the navigation bar in `templates/base.html` to use a vertical stacking behavior on small screens (using Bootstrap's navbar-expand classes or custom CSS).
- [x] Task: Ensure the main content container uses Bootstrap's responsive grid system correctly.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Core Layout & Navigation' (Protocol in workflow.md)

## Phase 2: Interface Responsiveness
- [x] Task: Update `templates/wbw.html`. d27b33b
    - [x] Sub-task: Wrap all tables in `div.table-responsive`. (No tables found, but checked)
    - [x] Sub-task: Ensure form groups use responsive classes (e.g., `col-12 col-md-6`) to stack on mobile and span on desktop.
- [x] Task: Update `templates/config.html`. ec85723
    - [x] Sub-task: Apply responsive classes to the configuration forms and tables.
    - [x] Sub-task: Ensure input fields and buttons are touch-friendly.
- [ ] Task: Update `templates/manual_upload.html` (and others) to ensure consistent table responsiveness.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Interface Responsiveness' (Protocol in workflow.md)

## Phase 3: Final Integration & Verification
- [ ] Task: Perform a comprehensive review of the application on various simulated mobile viewports (e.g., using browser dev tools).
- [ ] Task: Fix any identified spacing, font size, or overflow issues.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Integration & Verification' (Protocol in workflow.md)
