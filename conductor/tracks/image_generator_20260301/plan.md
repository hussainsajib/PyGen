# Implementation Plan: Image Post Generator

## Phase 1: Backend Core Logic (TDD)
Focus: Implementing the Pillow-based image composition engine with authentic Arabic and Bangla typography.

- [ ] Task: Define TDD tests for image generation (rendering accuracy, font resolution).
- [ ] Task: Implement `factories/image_generator.py` for base canvas (1080x1080) and background handling.
- [ ] Task: Integrate QPC v2 fonts for Arabic Ayah rendering with correct RTL flow.
- [ ] Task: Implement Bangla text rendering for translation and metadata (Surah/Ayah).
- [ ] Task: Implement branding watermark ("তাকওয়া বাংলা") in the bottom-right corner.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Backend Core Logic' (Protocol in workflow.md)

## Phase 2: API & Configuration (TDD)
Focus: Exposing generation logic via FastAPI and adding configurable social media metadata.

- [ ] Task: Define TDD tests for image endpoints and configuration retrieval.
- [ ] Task: Create FastAPI endpoints in `app.py` for `/api/generate-image` (preview) and `/api/download-image`.
- [ ] Task: Update global configuration and UI to support user-defined hashtags and post templates.
- [ ] Task: Implement image upload logic in `processes/facebook_utils.py` for Graph API integration.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: API & Configuration' (Protocol in workflow.md)

## Phase 3: Frontend UI Development
Focus: Building the React-based Image Generator interface and integrating it into the app.

- [ ] Task: Create `ImageGenerator` React component with Surah/Ayah selection and Unsplash integration.
- [ ] Task: Implement real-time preview and action buttons (Download, Post to Facebook).
- [ ] Task: Add "ইমেজ জেনারেটর" (Image Generator) to the main navigation bar.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Frontend UI Development' (Protocol in workflow.md)

## Phase 4: Integration & Polish
Focus: Final end-to-end testing, mobile optimization, and UI refinements.

- [ ] Task: Perform mobile responsiveness audit and fix layout issues.
- [ ] Task: Conduct full end-to-end manual verification (Select -> Customize -> Post).
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Integration & Polish' (Protocol in workflow.md)
