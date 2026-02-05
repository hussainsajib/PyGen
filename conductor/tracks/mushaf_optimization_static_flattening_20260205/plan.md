# Implementation Plan: Mushaf Video Generation Optimization (Static Flattening)

This plan outlines the steps to implement performance optimizations for Mushaf video generation, focusing on static layer flattening and font caching.

## Phase 1: Foundation and Performance Baseline [checkpoint: 8bf6c7d]
- [x] Task: Implement Ayah-range selection for Juz testing. [4abdcf2]
    - [ ] Update `generate_juz_video` in `processes/mushaf_video.py` to accept optional `start_ayah` and `end_ayah` overrides.
    - [ ] Add range filtering logic to ensure only specific Ayahs are processed during test runs.
    - [ ] Verify range selection works correctly by generating a 5-Ayah Juz segment.
- [x] Task: Implement Font Object Caching. [72ab263]
    - [ ] Write a benchmark test `tests/test_font_cache_perf.py` to measure rendering time with and without caching.
    - [ ] Implement a global `FONT_CACHE` dictionary in `factories/single_clip.py`.
    - [ ] Update `render_mushaf_text_to_image` to retrieve fonts from the cache based on path and size.
- [ ] Task: Conductor - User Manual Verification 'Foundation and Performance Baseline' (Protocol in workflow.md)

## Phase 2: Static Layer Flattening [checkpoint: 2cb27df]
- [x] Task: Develop the pre-rendering flattening engine. [438c88c]
- [x] Task: Refactor `generate_mushaf_page_clip` to use the flattened base. [30daa2e]
- [x] Task: Performance Validation. [30daa2e]
- [ ] Task: Conductor - User Manual Verification 'Static Layer Flattening' (Protocol in workflow.md)

## Phase 3: Robustness and Documentation
- [ ] Task: Final Regression and Documentation.
    - [ ] Verify that Surah-based Mushaf generation still functions correctly with the optimized engine.
    - [ ] Update `bottlenecks.md` with the new performance metrics and "Optimized" status for identified bottlenecks.
- [ ] Task: Conductor - User Manual Verification 'Robustness and Documentation' (Protocol in workflow.md)
