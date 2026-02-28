# Implementation Plan: High-Speed WBW Renderer

## Phase 1: Core Renderer Foundation [checkpoint: 2bddd24]
- [x] Task: Write failing unit tests for the base `WBWFastRenderer` initialization and frame generation. [dd07352]
- [x] Task: Implement the `WBWFastRenderer` skeleton in `factories/wbw_fast_render.py` using Pillow for text drawing. [21d3a72]
- [x] Task: Implement pre-rendering logic to generate and cache the base image (static text + background) for a scene. [21d3a72]
- [x] Task: Implement the `get_frame_at` method to apply dynamic highlight boxes over the cached base image. [2efb22c]
- [x] Task: Conductor - User Manual Verification 'Core Renderer Foundation' (Protocol in workflow.md) [2bddd24]

## Phase 2: Layout Logic & Visual Parity [checkpoint: c00397c]
- [x] Task: Write failing unit tests comparing `WBWFastRenderer` output against standard MoviePy frames for both Standard and Interlinear layouts. [c22d6b7]
- [x] Task: Implement Standard stacked layout logic (Arabic line + Translation line) with proper font sizing and shadows. [8069d4e]
- [x] Task: Implement Interlinear layout logic (word-over-translation) with solid underlines and precise word alignment. [b413f6c]
- [x] Task: Implement footer rendering (Reciter, Surah, Brand) within the fast renderer. [7eda545]
- [x] Task: Refine text drawing to match MoviePy's anti-aliasing and drop-shadow effects for perfect parity. [b69a681]
- [x] Task: Conductor - User Manual Verification 'Layout Logic & Visual Parity' (Protocol in workflow.md) [c00397c]

## Phase 3: Pipeline Integration & Advanced Backgrounds
- [ ] Task: Write failing integration tests for the `generate_wbw_fast` pipeline using the new renderer.
- [ ] Task: Update `processes/wbw_fast_video.py` to use `WBWFastRenderer` instead of `MoviePyRenderer`.
- [ ] Task: Implement support for video backgrounds by layering the fast-rendered text frames over video frames in the FFmpeg pipe.
- [ ] Task: Optimize the FFmpeg encoding parameters (presets, threads) for maximum throughput with the new renderer.
- [ ] Task: Conductor - User Manual Verification 'Pipeline Integration & Advanced Backgrounds' (Protocol in workflow.md)