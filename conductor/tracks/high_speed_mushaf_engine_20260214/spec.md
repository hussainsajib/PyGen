# Specification: High-Speed Mushaf Video Engine Comparison

## Overview
This feature focuses on evaluating high-speed alternatives to MoviePy for generating Mushaf videos. We will implement three distinct experimental backends using **FFmpeg**, **OpenCV**, and **PyAV** to determine which library provides the best balance of speed, memory efficiency, and visual fidelity.

## Functional Requirements
1.  **Three High-Speed Backends:**
    -   **FFmpeg Engine:** Implement video generation by pre-rendering frames with PIL and piping the sequence directly into a high-performance FFmpeg process.
    -   **OpenCV Engine:** Implement frame-by-frame composition and encoding using OpenCV's `VideoWriter`.
    -   **PyAV Engine:** Implement stream-based composition using the PyAV library for low-level control over FFmpeg's encoding capabilities.
2.  **Experimental Endpoints:**
    -   Create separate routes for each engine:
        -   `/create-mushaf-fast/ffmpeg`
        -   `/create-mushaf-fast/opencv`
        -   `/create-mushaf-fast/pyav`
3.  **Core Support:**
    -   Initially support both **Standalone Mushaf Videos** and **Juz Mushaf Videos**.
    -   Maintain exact visual parity with the existing MoviePy-based rendering (15-line layout, QPC v2 fonts, static Basmallah injection, etc.).
4.  **Performance Analytics:**
    -   Implement instrumentation to track and log the following for every generation job:
        -   **Total Generation Time (ms):** End-to-end duration.
        -   **Peak Memory Usage (MB):** Maximum RAM consumption during the process.
        -   **Visual Quality Parity:** Ensure text sharpness and color accuracy match the baseline.

## Non-Functional Requirements
-   **Execution Speed:** The target is a significant reduction in processing time compared to the current MoviePy engine.
-   **Reliability:** The new engines must handle long-form Juz videos (30+ minutes) without crashing or desynchronizing audio.

## Acceptance Criteria
-   [ ] Three functional endpoints are available for testing.
-   [ ] Each engine successfully produces a complete Mushaf video with accurate audio synchronization.
-   [ ] A performance report is generated for each job, clearly comparing generation time and memory usage.
-   [ ] Output videos are visually indistinguishable from the original MoviePy implementation.

## Out of Scope
-   Replacing the default MoviePy engine in this phase.
-   Implementing high-speed backends for Word-by-Word (non-Mushaf) videos.
