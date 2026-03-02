# Specification: Image Post Generator (Ayah & Bangla Translation)

## Overview
PyGen will be expanded to include a new "Image Post Generator" module. This feature will allow users to create visually appealing, square (1:1) images from specific Quranic verses (Ayat) and their corresponding Bangla translations, optimized for sharing on social media platforms like Facebook and Instagram. The feature will include a user interface for selection, background customization, and integrated uploading.

## Functional Requirements

### 1. User Interface (Frontend)
- **Navigation:** A new link "ইমেজ জেনারেটর" (Image Generator) will be added to the end of the primary navbar.
- **Selection Controls:**
    - Dropdowns to select Surah and Ayah number.
    - A search/upload interface for selecting a background image:
        - Support for local file upload.
        - Integration with the Unsplash API for searching high-quality stock images.
- **Content Inputs:**
    - A text area for the user to add a custom "Description" or "Caption" for the post.
- **Preview & Actions:**
    - A real-time (or near real-time) preview of the generated image.
    - A "ডাউনলোড" (Download) button to save the image to the local device.
    - An "ফেসবুকে পোস্ট করুন" (Post to Facebook) button to upload the image and its caption (user description + system hashtags) to the configured Facebook Page.

### 2. Image Generation (Backend)
- **Canvas:** Fixed 1080x1080 pixels (1:1 aspect ratio).
- **Layout Elements:**
    - **Background:** The selected image, possibly with a configurable dimming layer for readability (consistent with the video generator).
    - **Arabic Ayah:** Centered at the top/middle. Must use **QPC v2 (Mushaf Style)** fonts for authentic calligraphy, preserving RTL flow and logical glyph ordering.
    - **Bangla Translation:** Positioned below the Arabic text, using the project's **Default Bangla Font**.
    - **Metadata Line:** Positioned below the translation (e.g., "সূরা ফাতিহা:১"), localized in Bangla.
    - **Branding:** "তাকওয়া বাংলা" (Taqwa Bangla) placed in the bottom-right corner as a watermark.
- **Rendering Engine:** Utilize **Pillow (PIL)** for high-fidelity text rendering and composition, leveraging existing `font_utils.py` for font resolution.

### 3. Post Management & Upload
- **Caption Assembly:** Combine the user's custom description with a system-managed set of hashtags and links.
- **Configurable Hashtags:** Add a new section in the global settings to allow users to customize the default "base" hashtags and description template.
- **Social Media Integration:** Use the existing Facebook Graph API implementation (`processes/facebook_utils.py`) to handle image uploads to the designated Page.

## Non-Functional Requirements
- **Responsive Design:** The UI must be fully accessible on mobile devices.
- **Performance:** Image generation should be optimized for low latency to provide a responsive preview.

## Acceptance Criteria
- User can select a Surah/Ayah and see a preview with authentic Arabic calligraphy (QPC v2).
- User can upload or search (Unsplash) for a background image.
- The metadata (Surah name/Ayah number) and branding are correctly localized in Bangla.
- The generated image can be downloaded in high resolution (1080x1080).
- The image and its full caption (including hashtags) can be successfully uploaded to the configured Facebook Page.
- The "Image Generator" link is visible and functional in the navbar.

## Out of Scope
- Video generation (already exists).
- Generating multiple images in a carousel/bulk mode in the first iteration.
- Direct posting to Instagram (unless handled via Facebook's Cross-Posting, which is outside the scope of the PyGen integration itself).
