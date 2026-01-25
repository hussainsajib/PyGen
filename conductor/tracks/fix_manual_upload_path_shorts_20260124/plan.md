# Plan: Fix Manual Upload Path for Shorts

## Phase 1: Investigation and Infrastructure
- [x] Task: Locate the specific code responsible for the `Manual Upload` YouTube integration. (Likely in `app.py` or `processes/youtube_utils.py`).
- [x] Task: Identify how the system distinguishes between "Shorts" and "Standard Videos" in the `Manual Upload` view.
- [~] Task: Conductor - User Manual Verification 'Phase 1: Investigation and Infrastructure' (Protocol in workflow.md)

## Phase 2: Bug Fix and Testing [checkpoint: ba2699f]
- [x] Task: Create a reproduction test case in `tests/test_manual_upload.py` (or a new test file) that simulates an upload attempt for a file in the `shorts/` directory. 9884701
- [x] Task: Implement a path resolution utility or update existing logic to switch between `exported_data/videos` and `exported_data/shorts` based on the file type/prefix. 7778375
- [x] Task: Verify the fix by running the newly created tests and ensuring they pass. 7778375
- [x] Task: Conductor - User Manual Verification 'Phase 2: Bug Fix and Testing' (Protocol in workflow.md) ba2699f

## Phase 3: Integration and Verification
- [ ] Task: Perform a manual verification by attempting to upload the specific file `quran_shorts_2_127_129_maher_al_muaiqly.mp4` through the web UI.
- [ ] Task: Verify that standard videos can still be uploaded from the `videos/` directory without issue.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Integration and Verification' (Protocol in workflow.md)
