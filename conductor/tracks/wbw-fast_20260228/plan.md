# Implementation Plan: WBW (Fast) Video Generation Endpoint

## Phase 1: Backend Integration & Route Setup
- [x] Task: Write failing integration tests for the new "WBW (Fast)" endpoint and form submission. [00ae414]
- [x] Task: Implement a new FastAPI route (e.g., `/wbw-fast`) that serves the new UI. [3ac7591]
- [x] Task: Modify the job submission logic in the new route to inject an `engine='ffmpeg'` flag (or equivalent identifier) into the queued job payload. [3ac7591]
- [x] Task: Update the background worker to parse the `engine` flag and route the generation task to the FFmpeg engine. [480c979]
- [x] Task: Conductor - User Manual Verification 'Backend Integration & Route Setup' (Protocol in workflow.md)

## Phase 2: User Interface & Frontend Form
- [x] Task: Write failing UI unit tests or e2e test stubs for the new "WBW (Fast)" form layout. [0cb0e31]
- [x] Task: Create a new Jinja2 template for the simplified WBW interface, retaining intro, outro, background, and highlight settings, while removing unsupported ones. [3ac7591]
- [x] Task: Update the main navigation bar to include the "WBW (Fast)" link pointing to the new route. [99ec1b0]
- [x] Task: Ensure form submission correctly serializes and passes all required settings to the backend endpoint. [0cb0e31]
- [ ] Task: Conductor - User Manual Verification 'User Interface & Frontend Form' (Protocol in workflow.md)

## Phase 3: Engine Integration & Feature Parity
- [ ] Task: Write failing unit/integration tests to verify intro, outro, background, and highlight generation using the FFmpeg engine specifically.
- [ ] Task: Update the FFmpeg engine pipeline to correctly process and incorporate intro and outro screens.
- [ ] Task: Ensure static image and stock video backgrounds are correctly layered within the FFmpeg pipeline.
- [ ] Task: Verify that word-by-word highlights are accurately calculated and synchronized when using the FFmpeg backend.
- [ ] Task: Conductor - User Manual Verification 'Engine Integration & Feature Parity' (Protocol in workflow.md)