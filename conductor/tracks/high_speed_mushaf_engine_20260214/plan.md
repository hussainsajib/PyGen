# Implementation Plan: High-Speed Mushaf Video Engine Comparison

## Phase 1: Rendering Abstraction & Instrumentation
Establish a shared rendering base and tools to measure performance accurately across all engines.

- [x] Task: Write unit tests for shared PIL rendering utilities in `tests/test_fast_render_base.py`. dee0446
- [x] Task: Refactor existing PIL rendering logic into a modular component that can provide raw frames to different backends. 3448a65
- [x] Task: Implement a `PerformanceMonitor` utility to track execution time and peak memory usage (RSS). a3b02d0
- [x] Task: Conductor - User Manual Verification 'Rendering Abstraction & Instrumentation' (Protocol in workflow.md) a3b02d0

## Phase 2: FFmpeg Backend Implementation
Implement the first high-speed backend using FFmpeg's piped sequence approach.

- [ ] Task: Write integration tests for FFmpeg engine generation in `tests/test_ffmpeg_engine.py`.
- [ ] Task: Implement the `FFmpegEngine` that pre-renders frames and pipes them to an FFmpeg subprocess.
- [ ] Task: Verify audio synchronization and video container integrity for the FFmpeg output.
- [ ] Task: Conductor - User Manual Verification 'FFmpeg Backend Implementation' (Protocol in workflow.md)

## Phase 3: OpenCV Backend Implementation
Implement the second high-speed backend using OpenCV's native VideoWriter.

- [ ] Task: Write integration tests for OpenCV engine generation in `tests/test_opencv_engine.py`.
- [ ] Task: Implement the `OpenCVEngine` using `cv2.VideoWriter`.
- [ ] Task: Verify audio synchronization (merging video with audio using FFmpeg after initial encoding).
- [ ] Task: Conductor - User Manual Verification 'OpenCV Backend Implementation' (Protocol in workflow.md)

## Phase 4: PyAV Backend Implementation
Implement the third high-speed backend using the PyAV library for low-level stream control.

- [ ] Task: Write integration tests for PyAV engine generation in `tests/test_pyav_engine.py`.
- [ ] Task: Implement the `PyAVEngine` to manage streams, packets, and encoding directly.
- [ ] Task: Verify audio synchronization and visual parity for the PyAV output.
- [ ] Task: Conductor - User Manual Verification 'PyAV Backend Implementation' (Protocol in workflow.md)

## Phase 5: API & UI Integration
Expose the three engines via separate endpoints and update the interface for testing.

- [ ] Task: Create FastAPI routes for `/create-mushaf-fast/{engine}`.
- [ ] Task: Update the Mushaf and Juz video creation templates to include an "Engine" selection dropdown (Experimental).
- [ ] Task: Implement automated logging of performance metrics into the job results.
- [ ] Task: Conductor - User Manual Verification 'API & UI Integration' (Protocol in workflow.md)

## Phase 6: Benchmark & Finalization
Compare the results and finalize the experimental module.

- [ ] Task: Run a standardized benchmark suite (Surah 108 vs. Juz 30) across all 4 engines (MoviePy + 3 new).
- [ ] Task: Update project documentation with performance findings and visual parity reports.
- [ ] Task: Conductor - User Manual Verification 'Benchmark & Finalization' (Protocol in workflow.md)
