# Implementation Plan: Mushaf Video Generation Optimization (Static Flattening)

This plan outlines the steps to implement performance optimizations for Mushaf video generation, focusing on static layer flattening and font caching.

## Phase 1: Foundation and Performance Baseline
- [x] Task: Implement Ayah-range selection for Juz testing. [4abdcf2]
    - [ ] Update `generate_juz_video` in `processes/mushaf_video.py` to accept optional `start_ayah` and `end_ayah` overrides.
    - [ ] Add range filtering logic to ensure only specific Ayahs are processed during test runs.
    - [ ] Verify range selection works correctly by generating a 5-Ayah Juz segment.
- [ ] Task: Implement Font Object Caching.
    - [ ] Write a benchmark test `tests/test_font_cache_perf.py` to measure rendering time with and without caching.
    - [ ] Implement a global `FONT_CACHE` dictionary in `factories/single_clip.py`.
    - [ ] Update `render_mushaf_text_to_image` to retrieve fonts from the cache based on path and size.
- [ ] Task: Conductor - User Manual Verification 'Foundation and Performance Baseline' (Protocol in workflow.md)

## Phase 2: Static Layer Flattening
- [ ] Task: Develop the pre-rendering flattening engine.
    - [ ] Create a helper function `pre_render_static_page` in `factories/single_clip.py` that composites the background, border, header, and ayah text onto a single PIL Image.
    - [ ] Write unit tests in `tests/test_mushaf_flattening.py` to ensure the generated image dimensions and text placements match the current multi-layer layout.
- [ ] Task: Refactor `generate_mushaf_page_clip` to use the flattened base.
    - [ ] Replace the individual `ImageClip` layers for background, border, and static text with a single `ImageClip` from the pre-rendered buffer.
    - [ ] Ensure dynamic layers (highlighting `ColorClips` and the progress bar) are correctly overlayed on top of the flattened base.
- [ ] Task: Performance Validation.
    - [ ] Run a benchmark generation for Surah 108 using the optimized engine.
    - [ ] Compare the "Performance Ratio" against the baseline documented in `bottlenecks.md`.
- [ ] Task: Conductor - User Manual Verification 'Static Layer Flattening' (Protocol in workflow.md)

## Phase 3: Robustness and Documentation
- [ ] Task: Final Regression and Documentation.
    - [ ] Verify that Surah-based Mushaf generation still functions correctly with the optimized engine.
    - [ ] Update `bottlenecks.md` with the new performance metrics and "Optimized" status for identified bottlenecks.
- [ ] Task: Conductor - User Manual Verification 'Robustness and Documentation' (Protocol in workflow.md)
