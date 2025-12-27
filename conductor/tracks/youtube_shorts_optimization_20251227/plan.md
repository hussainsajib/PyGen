# Implementation Plan: YouTube Shorts Optimization for WBW Videos

## Phase 1: Upload Logic Refinement
- [x] Task: Implement video duration validation and Shorts metadata enhancement
    - [x] Sub-task: Write failing tests for duration validation logic (checking < 180s and > 180s cases).
    - [x] Sub-task: Update `upload_to_youtube` in `processes/youtube_utils.py` to calculate video duration and conditionally apply `#Shorts` to title, description, and tags.
- [~] Task: Conductor - User Manual Verification 'Phase 1: Upload Logic Refinement' (Protocol in workflow.md)

## Phase 2: Integration and Final Verification
- [ ] Task: End-to-end verification of Shorts upload
    - [ ] Sub-task: Generate a short WBW video (< 180s) and verify the YouTube upload metadata includes `#Shorts`.
    - [ ] Sub-task: Generate a long WBW video (> 180s) and verify it is uploaded as a regular video without `#Shorts`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Integration and Final Verification' (Protocol in workflow.md)
