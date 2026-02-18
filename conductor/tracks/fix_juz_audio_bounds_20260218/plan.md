# Implementation Plan: Fix Out-of-Bounds Audio Access in Juz Mushaf Generation

## Phase 1: Research & Reproduction [checkpoint: 8b2ce0a]
- [x] Task: Create a reproduction script `repro_juz_audio_bounds.py` that simulates Juz 30 Shuraym audio concatenation and timestamp mapping.
- [x] Task: Identify the exact line in `processes/mushaf_video.py` or `factories/mushaf_ffmpeg_engine.py` (assuming high-speed FFmpeg was used) where the out-of-bounds access occurs.
- [x] Task: Conductor - User Manual Verification 'Research & Reproduction' (Protocol in workflow.md) (8b2ce0a)

## Phase 2: Implementation (TDD) [checkpoint: 582f828]
- [x] Task: Write failing tests in `tests/test_juz_audio_sync.py` that simulate floating-point drift in long-form audio concatenation.
- [x] Task: Implement a "padding" or "clamping" mechanism in the audio concatenation logic to ensure audio duration >= max timestamp.
- [x] Task: Refine `get_wbw_timestamps` and mapping logic to use decimal precision or robust rounding to prevent drift.    
- [x] Task: Verify that all tests pass and coverage is maintained.
- [x] Task: Conductor - User Manual Verification 'Implementation' (Protocol in workflow.md) (582f828)
## Phase 3: Final Integration & Verification [checkpoint: 3ddf0ba]
- [x] Task: Run a full Juz 30 generation for Reciter Shuraym using the high-speed FFmpeg engine.
- [x] Task: Manually inspect the end of the video to ensure audio doesn't cut off and highlights stay aligned.
- [x] Task: Conductor - User Manual Verification 'Final Integration & Verification' (Protocol in workflow.md) (3ddf0ba)
