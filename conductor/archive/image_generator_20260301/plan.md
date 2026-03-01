# Implementation Plan: Image Post Generator

## Phase 1: Backend Core Logic (TDD) [checkpoint: 864057e]
Focus: Implementing the Pillow-based image composition engine with authentic Arabic and Bangla typography.

- [x] Task: Define TDD tests for image generation (rendering accuracy, font resolution).
- [ ] Task: Implement `factories/image_generator.py` for base canvas (1080x1080) and background handling.
- [x] Task: Integrate QPC v2 fonts for Arabic Ayah rendering with correct RTL flow.
- [x] Task: Implement Bangla text rendering for translation and metadata (Surah/Ayah).
- [x] Task: Implement branding watermark ("à¦¤à¦¾à¦•à¦“à¦¯à¦¼à¦¾ à¦¬à¦¾à¦‚à¦²à¦¾") in the bottom-right corner.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Backend Core Logic' (Protocol in workflow.md)

## Phase 2: API & Configuration (TDD) [checkpoint: 030083c]
Focus: Exposing generation logic via FastAPI and adding configurable social media metadata.

- [x] Task: Define TDD tests for image endpoints and configuration retrieval.
- [ ] Task: Create FastAPI endpoints in `app.py` for `/api/generate-image` (preview) and `/api/download-image`.
- [~] Task: Update global configuration and UI to support user-defined hashtags and post templates.
- [x] Task: Implement image upload logic in `processes/facebook_utils.py` for Graph API integration.
- [x] Task: Conductor - User Manual Verification 'Phase 2: API & Configuration' (Protocol in workflow.md)

## Phase 3: Frontend UI Development [checkpoint: bda1f8b]
Focus: Building the React-based Image Generator interface and integrating it into the app.

- [ ] Task: Create `ImageGenerator` React component with Surah/Ayah selection and Unsplash integration.
- [ ] Task: Implement real-time preview and action buttons (Download, Post to Facebook).
- [ ] Task: Add "à¦‡à¦®à§‡à¦œ à¦œà§‡à¦¨à¦¾à¦°à§‡à¦Ÿà¦°" (Image Generator) to the main navigation bar.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Frontend UI Development' (Protocol in workflow.md)

## Phase 4: Integration & Polish [checkpoint: cab9c1d]
Focus: Final end-to-end testing, mobile optimization, and UI refinements.

- [x] Task: Perform mobile responsiveness audit and fix layout issues.
- [x] Task: Conduct full end-to-end manual verification (Select -> Customize -> Post).
- [x] Task: Conductor - User Manual Verification 'Phase 4: Integration & Polish' (Protocol in workflow.md)
