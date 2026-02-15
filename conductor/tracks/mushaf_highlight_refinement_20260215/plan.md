# Implementation Plan: Mushaf Video Highlighting & Integration Refinement

## Phase 1: Highlighting Fix & Visual Verification
Investigate and resolve the transparency issue in Mushaf highlighting.

- [x] Task: Create a visual reproduction script `scripts/reproduce_highlight_issue.py` to generate single-frame specimens of the highlight across all engines. 550fdac
- [x] Task: Investigate PIL alpha-blending logic in `factories/mushaf_fast_render.py` and `factories/single_clip.py`. 550fdac
- [x] Task: Implement the fix for highlight transparency (ensuring `Image.alpha_composite` or equivalent is used correctly). 550fdac
- [x] Task: Conductor - User Manual Verification 'Highlighting Fix & Visual Verification' (Protocol in workflow.md) 550fdac

## Phase 2: Terminal Logging & Metadata Generation [checkpoint: 401e133]
Improve developer visibility by logging paths and ensuring metadata completeness.

- [x] Task: Update `processes/mushaf_video.py` and `processes/mushaf_fast_video.py` to print relative export paths to the terminal. 401e133
- [x] Task: Verify that all high-speed engines (FFmpeg, OpenCV, PyAV) generate the `.txt` details file in `exported_data/details`. 401e133
- [x] Task: Write unit tests in `tests/test_fast_metadata.py` to verify metadata file existence after generation. 401e133
- [x] Task: Conductor - User Manual Verification 'Terminal Logging & Metadata Generation' (Protocol in workflow.md) 401e133

## Phase 3: Social Media Upload Connectivity [checkpoint: e5b30fc]
Verify and fix the integration between high-speed engines and automated uploaders.

- [x] Task: Audit `app.py` route parameters to ensure `upload_after_generation` is correctly passed for fast engine routes. e5b30fc
- [x] Task: Update `processes/background_worker.py` to handle post-generation upload triggers for the `mushaf_fast` job type. e5b30fc
- [x] Task: Test end-to-end connectivity (Generation -> Metadata -> Upload Trigger) using a mock uploader. e5b30fc
- [x] Task: Conductor - User Manual Verification 'Social Media Upload Connectivity' (Protocol in workflow.md) e5b30fc

## Phase 4: Final Verification & Documentation
Final checks and documentation sync.

- [~] Task: Run a full Juz 30 benchmark using the FFmpeg engine and verify highlights and terminal output.
- [ ] Task: Update project documentation if any new logging flags or config interactions were introduced.
- [ ] Task: Conductor - User Manual Verification 'Final Verification & Documentation' (Protocol in workflow.md)
