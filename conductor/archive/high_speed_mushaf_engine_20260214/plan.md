# Implementation Plan: High-Speed Mushaf Video Engine Comparison

## Phase 1: Rendering Abstraction & Instrumentation [checkpoint: e3bfb97]
Establish a shared rendering base and tools to measure performance accurately across all engines.

- [x] Task: Write unit tests for shared PIL rendering utilities in `tests/test_fast_render_base.py`. dee0446
- [x] Task: Refactor existing PIL rendering logic into a modular component that can provide raw frames to different backends. 3448a65
- [x] Task: Implement a `PerformanceMonitor` utility to track execution time and peak memory usage (RSS). a3b02d0
- [x] Task: Conductor - User Manual Verification 'Rendering Abstraction & Instrumentation' (Protocol in workflow.md) a3b02d0

## Phase 2: FFmpeg Backend Implementation [checkpoint: 89877c6]
Implement the first high-speed backend using FFmpeg's piped sequence approach.

- [x] Task: Write integration tests for FFmpeg engine generation in `tests/test_ffmpeg_engine.py`. 89877c6
- [x] Task: Implement the `FFmpegEngine` that pre-renders frames and pipes them to an FFmpeg subprocess. 89877c6
- [x] Task: Verify audio synchronization and video container integrity for the FFmpeg output. 89877c6
- [x] Task: Conductor - User Manual Verification 'FFmpeg Backend Implementation' (Protocol in workflow.md) 89877c6

## Phase 3: OpenCV Backend Implementation [checkpoint: 4f9fb3f]
Implement the second high-speed backend using OpenCV's native VideoWriter.

- [x] Task: Write integration tests for OpenCV engine generation in `tests/test_opencv_engine.py`. 4f9fb3f
- [x] Task: Implement the `OpenCVEngine` using `cv2.VideoWriter`. 4f9fb3f
- [x] Task: Verify audio synchronization (merging video with audio using FFmpeg after initial encoding). 4f9fb3f
- [x] Task: Conductor - User Manual Verification 'OpenCV Backend Implementation' (Protocol in workflow.md) 4f9fb3f

## Phase 4: PyAV Backend Implementation [checkpoint: 476000c]
Implement the third high-speed backend using the PyAV library for low-level stream control.

- [x] Task: Write integration tests for PyAV engine generation in `tests/test_pyav_engine.py`. 476000c
- [x] Task: Implement the `PyAVEngine` to manage streams, packets, and encoding directly. 476000c
- [x] Task: Verify audio synchronization and visual parity for the PyAV output. 476000c
- [x] Task: Conductor - User Manual Verification 'PyAV Backend Implementation' (Protocol in workflow.md) 476000c

## Phase 5: API & UI Integration [checkpoint: 0b0bebf]
Expose the three engines via separate endpoints and update the interface for testing.

- [x] Task: Create FastAPI routes for `/create-mushaf-fast/{engine}`. 0b0bebf
- [x] Task: Update the Mushaf and Juz video creation templates to include an "Engine" selection dropdown (Experimental). 0b0bebf
- [x] Task: Implement automated logging of performance metrics into the job results. 0b0bebf
- [x] Task: Conductor - User Manual Verification 'API & UI Integration' (Protocol in workflow.md) 0b0bebf

## Phase 6: Benchmark & Finalization [checkpoint: 0b0bebf]
Compare the results and finalize the experimental module.

- [x] Task: Run a standardized benchmark suite (Surah 108 vs. Juz 30) across all 4 engines (MoviePy + 3 new). 0b0bebf
- [x] Task: Update project documentation with performance findings and visual parity reports. 0b0bebf
- [x] Task: Conductor - User Manual Verification 'Benchmark & Finalization' (Protocol in workflow.md) 0b0bebf
