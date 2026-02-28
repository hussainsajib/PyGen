# Specification: High-Speed WBW Renderer (Pillow/OpenCV)

## Overview
The current "WBW (Fast)" implementation is suboptimal because it still relies on MoviePy's heavy clip composition, simply piping the output to FFmpeg. This track will replace that logic with a dedicated `WBWFastRenderer` using Pillow and OpenCV to bypass the overhead of MoviePy's layer processing. This is expected to provide a 10x-40x speedup by utilizing pre-rendering and caching techniques.

## Functional Requirements
- **Specialized Renderer:** Implement a `WBWFastRenderer` class that handles the layout and drawing of Arabic text and translations directly using `Pillow` (for high-quality typography) and `OpenCV` (for high-speed frame manipulation).
- **Pre-rendering & Caching:** 
    - For each line/scene, pre-render a "Base Image" containing the background and all static text (Arabic + Translation).
    - Cache this base image in memory.
    - For each video frame, perform a shallow copy of the base image and draw only the active word's highlight box.
- **Layout Support:** 
    - **Standard Layout:** Stacked Arabic and Translation lines.
    - **Interlinear Layout:** Word-over-translation rendering with proper alignment and solid underlines.
- **Feature Parity (Visual):** Match the existing MoviePy output style exactly, including:
    - Font faces, sizes, and colors.
    - Text drop shadows/glows.
    - Highlight box transparency and color.
    - Dynamic footer (Reciter, Surah, Brand info).
- **Background Support:**
    - **Static Images:** Supported with pre-rendering.
    - **Video Backgrounds:** Supported by drawing text overlays on top of the underlying video frames in real-time.
- **Pipeline Integration:** Update the `generate_wbw_fast` pipeline to use this new renderer instead of the `MoviePyRenderer` wrapper.

## Non-Functional Requirements
- **Performance:** Target rendering speeds significantly faster than the current MoviePy-based approach (aiming for near real-time or faster).
- **Maintainability:** Ensure the layout logic is encapsulated and doesn't duplicate complex segmentation logic unnecessarily.

## Acceptance Criteria
- [ ] A `WBWFastRenderer` class exists and successfully generates frames for both standard and interlinear layouts.
- [ ] The visual output of the fast renderer is indistinguishable from the standard MoviePy renderer.
- [ ] Video generation for a standard surah/verse range is measurably faster (e.g., >10x speedup) than the MoviePy equivalent.
- [ ] Intro/Outro screens and backgrounds are correctly handled by the fast pipeline.
- [ ] High-speed mode works correctly with both static image and video backgrounds.

## Out of Scope
- Replacing the renderer for the standard "Word-by-Word" creation page (this track targets the "WBW (Fast)" endpoint only).
- Migrating Intro/Outro generation to Pillow/OpenCV (these can remain MoviePy clips for now as they are rendered once per video).