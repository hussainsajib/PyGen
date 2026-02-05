# Specification: Mushaf Video Generation Performance Investigation

## Overview
This investigation aims to identify the root causes of slow performance in the Mushaf video generation engine. The current process, primarily handled in `processes/mushaf_video.py` and `factories/single_clip.py`, is perceived as inefficient. This track will focus on profiling the existing logic to pinpoint bottlenecks and providing a roadmap for optimization.

## Goals
- Identify specific functions or processes within the Mushaf video generation workflow that contribute most significantly to latency.
- Quantify the performance impact of text rendering, clip compositing, and video encoding.
- Provide actionable recommendations for speeding up video generation.

## Functional Requirements
- **Performance Profiling:**
    - Measure execution time for `render_mushaf_text_to_image` (Pillow-based rendering).
    - Measure overhead of `CompositeVideoClip` assembly for a standard Mushaf page.
    - Monitor system resource usage (CPU/GPU/Memory) during the `write_videofile` phase.
- **Reporting:**
    - Create a `bottlenecks.md` file in the project root or the track directory.
    - Document findings with specific metrics and logs where applicable.
    - Provide a prioritized list of optimization strategies (e.g., caching, parallelization, alternative libraries).

## Non-Functional Requirements
- **Minimal Impact:** The investigation should not introduce significant changes to the existing production code unless necessary for profiling.
- **Reproducibility:** Use a standard surah/reciter combination for all benchmarks (e.g., Surah 108 with Alafasy).

## Acceptance Criteria
- [ ] A `bottlenecks.md` report is created.
- [ ] The report identifies at least three specific areas for optimization.
- [ ] The report includes quantitative data (timing, resource usage) to support the findings.
- [ ] Recommendations are prioritized by estimated impact vs. implementation effort.

## Out of Scope
- Implementing the recommended optimizations (this will be handled in subsequent tracks).
- Investigating Word-by-Word (WBW) video generation performance (unless logic is shared).
- Hardware upgrades or cloud infrastructure changes.
