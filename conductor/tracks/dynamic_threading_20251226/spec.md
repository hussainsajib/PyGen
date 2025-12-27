# Track Specification: Dynamic and Standardized Threading for Video Encoding

## Overview
This track aims to standardize and optimize the video encoding process by replacing hardcoded thread counts with a dynamic, system-aware configuration. This ensures better performance across different hardware while maintaining system responsiveness.

## Functional Requirements
- **Global Thread Configuration:** Introduce a centralized constant for video encoding threads.
- **Dynamic Calculation:** The thread count must be calculated at runtime based on the system's CPU cores.
- **Resource Balancing:** By default, use `N-1` cores (where N is the total CPU count) to ensure the system remains responsive during the encoding process.
- **Universal Application:** Apply this dynamic setting to both standard surah video generation and word-by-word (WBW) video generation.

## Technical Requirements
- **Configuration Centralization:** Add `VIDEO_ENCODING_THREADS` to `processes/video_configs.py`.
- **System Inspection:** Use `os.cpu_count()` to determine available resources.
- **Code Refactoring:**
    - Update `processes/surah_video.py` to use the new constant in `write_videofile`.
    - Update `processes/video_utils.py` to use the new constant in `write_videofile`.

## Acceptance Criteria
- [ ] Hardcoded thread values (`threads=4`, `threads=6`) are removed from the codebase.
- [ ] Both `generate_surah` and `generate_video` use the centralized `VIDEO_ENCODING_THREADS` setting.
- [ ] The thread count defaults to `max(1, os.cpu_count() - 1)`.
- [ ] Video generation completes successfully for both standard and WBW paths.

## Out of Scope
- Adding a UI toggle to manually override the thread count (this remains a code-level configuration for now).
- Optimizing other MoviePy parameters (e.g., preset, bitrate).
