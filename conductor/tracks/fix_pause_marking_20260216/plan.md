# Implementation Plan: Fix Pause Marking Positioning in Mushaf/Juz Videos

## Phase 1: Investigation and Reproduction
- [ ] Task: Identify reproduction scripts or create a new test script to generate Mushaf clips for Surah 110:3 and Surah 2:5.
- [ ] Task: Verify the current incorrect rendering (pause sign on the right) using the default MoviePy engine.
- [ ] Task: Locate the exact text assembly logic in `factories/single_clip.py` and other engine factories (`factories/mushaf_ffmpeg_engine.py`, etc.).
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Investigation and Reproduction' (Protocol in workflow.md)

## Phase 2: Core Fix Implementation (MoviePy)
- [ ] Task: Write failing unit tests in `tests/test_mushaf_rendering.py` that check the character order for lines containing pause signs.
- [ ] Task: Modify the text concatenation logic in `factories/single_clip.py` to correctly handle PUA glyphs and pause sign positioning.
- [ ] Task: Verify the fix in `factories/single_clip.py` by running the reproduction script and checking the output image/video.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Core Fix Implementation (MoviePy)' (Protocol in workflow.md)

## Phase 3: High-Speed Engine Parity
- [ ] Task: Audit `factories/mushaf_ffmpeg_engine.py`, `factories/mushaf_opencv_engine.py`, and `factories/mushaf_pyav_engine.py` for similar assembly logic.
- [ ] Task: Apply the fix to all high-speed engines to ensure consistent behavior across the platform.
- [ ] Task: Verify the fix for at least one high-speed engine (e.g., FFmpeg) using the reproduction script.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: High-Speed Engine Parity' (Protocol in workflow.md)

## Phase 4: Integration and Final Verification
- [ ] Task: Run the full test suite to ensure no regressions in standard word-by-word videos or other Mushaf components.
- [ ] Task: Perform a final visual check of a full Juz video segment to ensure general layout stability.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Integration and Final Verification' (Protocol in workflow.md)
