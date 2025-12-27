# Implementation Plan: Word-by-Word UX and Layout Refinements

## Phase 1: Engine and Positioning Adjustments
- [ ] Task: Shift full translation overlay upward
    - [ ] Sub-task: Update `get_full_ayah_translation_position` in `processes/video_configs.py` to move the Y position up by an additional 50 pixels for both short and long videos.
- [ ] Task: Update redirect logic for WBW jobs
    - [ ] Sub-task: Modify the `create_video` endpoint in `app.py` to check if `job_type` is 'wbw' and redirect the user back to the `/word-by-word` page instead of the index.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Engine and Positioning Adjustments' (Protocol in workflow.md)

## Phase 2: Frontend UI Enhancements [checkpoint: 5394fae]
- [x] Task: Expose default color configurations to WBW template
    - [x] Sub-task: Update the `wbw_interface` route in `app.py` to include `BACKGROUND_RGB` and `FONT_COLOR` from the configuration manager in the template context.
- [x] Task: Implement "Default Color" reset button
    - [x] Sub-task: Modify `templates/wbw.html` to add the "Default Color" button next to the background selection button.
    - [x] Sub-task: Add JavaScript logic to `wbw.html` to clear the `active_background` value and reset the UI display when the button is clicked.
    - [x] Sub-task: Apply dynamic styling to the button using the passed configuration colors.
- [x] Task: Refine "Default Color" UI and logic
    - [x] Sub-task: Remove redundant "Default Color" text next to the reset button in `templates/wbw.html`.
    - [x] Sub-task: Update `/clear-active-background` in `app.py` to set the configuration value to an empty string instead of deleting the key.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Frontend UI Enhancements' [5394fae] (Protocol in workflow.md)

## Phase 3: Integration and Final Verification
- [ ] Task: End-to-end flow test
    - [ ] Sub-task: Generate a WBW video, verify the new overlay height, and confirm the redirect lands on the correct page.
    - [ ] Sub-task: Verify the "Default Color" button correctly resets background selections in the browser.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Integration and Final Verification' (Protocol in workflow.md)
