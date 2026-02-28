# Specification: WBW (Fast) Video Generation Endpoint

## Overview
This track implements a high-performance replica of the Word-by-Word (WBW) video generation feature using the FFmpeg encoding engine instead of the standard MoviePy engine. A new dedicated endpoint and user interface, accessible via the navbar as "WBW (Fast)", will be created to allow users to generate WBW videos quickly.

## Functional Requirements
- **Navbar Integration:** Add a new link titled "WBW (Fast)" to the application's main navigation bar.
- **Dedicated User Interface:** Create a new page/endpoint for the "WBW (Fast)" generator. 
    - The UI should be a simplified version of the existing WBW generator, stripping away settings that are irrelevant or unsupported by the FFmpeg engine.
- **Video Generation Engine:** Utilize FFmpeg (Piped/High-Speed engine) for video rendering on this endpoint.
- **Backend Integration:** Seamlessly integrate with the existing job queue system. When jobs are submitted from the "WBW (Fast)" endpoint, they should carry a flag forcing the backend to use the FFmpeg engine instead of the default.
- **Feature Parity:** The FFmpeg generation pipeline MUST support the following features:
    - Addition of Intro and Outro screens.
    - Support for both static images and stock video backgrounds.
    - Word-by-word highlighting effects synchronized with the recitation.

## Non-Functional Requirements
- **Performance:** Rendering speed should be significantly faster than the existing MoviePy-based WBW generation.
- **Maintainability:** Reuse the existing job queue and rendering infrastructure where possible to avoid code duplication.

## Acceptance Criteria
- [ ] The user can click a "WBW (Fast)" link in the navbar.
- [ ] The user is taken to a simplified WBW video generation interface.
- [ ] The user can configure a WBW video with an intro, outro, background (image/video), and highlighting.
- [ ] Submitting the form successfully queues a job.
- [ ] The background worker processes the job using the high-speed FFmpeg engine exclusively.
- [ ] The final output video accurately renders the word-by-word text, highlights, background, and intro/outro.
- [ ] The video generation time is measurably lower than the equivalent MoviePy generation.

## Out of Scope
- Complete removal or replacement of the existing MoviePy WBW generator.
- Support for complex visual effects or features not currently supported by the experimental FFmpeg backend.
- Creating a completely separate job queue for these tasks.