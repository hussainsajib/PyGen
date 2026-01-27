# Implementation Plan: Unified Video Customizable Backgrounds

This plan details the steps to implement a unified background selection system for both Mushaf and WBW video generation.

## Phase 1: Engine & API Updates
- [x] Task: Modify `factories/single_clip.py` to support custom hex color backgrounds.
    - Update `generate_background` to handle hex strings.
    - If a hex string is provided, use `generate_solid_background`.
- [x] Task: Update the creation API endpoints in `app.py`.
    - Ensure both Mushaf and WBW endpoints accept a `background_color` parameter.
- [x] Task: Conductor - User Manual Verification 'Engine Updates' (Protocol in workflow.md)

## Phase 2: UI Synchronization
- [x] Task: Update Mushaf and WBW creation templates.
    - Integrate a color picker or text input for hex codes in the background selection area.
    - Ensure the UI handles the mutually exclusive choice between media and solid color correctly.
- [x] Task: Conductor - User Manual Verification 'UI Sync' (Protocol in workflow.md)

## Phase 3: Verification
- [x] Task: Run `scripts/verify_mushaf_rendering.py` with a custom background color.
- [x] Task: Manually generate a WBW video with a custom background color and verify.
