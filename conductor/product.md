# Initial Concept
I want to build a new feature that let's me upload existing generated video to youtube that hasn't already been uploaded. for this. the video itself can be found inside exported_data/videos, the screenshot can be found inside exported_data/screenshots, and details to be attached to the video inside exported_data/details. The detail files are namee in this format: {surah_number}_{start_ayah}_{end_ayah}_{reciter}.txt. The screenshots follow this pattern: screenshot_quran_video_{surah_number}_{reciter}.png. The videos follow this patter: quran_video_{surah_number}_{reciter}.mp4. create a new endpoint where I can see all the video files, whether they have details file and screenshots, show the reciter name, if that reciter has a playlist available in youtube and a button to upload that the youtube

# PyGen Product Guide

## Overview
PyGen is an automated video generation platform designed specifically for creating high-quality Islamic content. It streamlines the process of combining Quranic recitations, translations, and customizable visual elements into engaging videos for social media and educational purposes.

## Target Audience
- **Individual Content Creators:** Users who want to share Islamic reminders and recitations on platforms like YouTube, Instagram, and TikTok without needing professional video editing skills.

## Core Goals
- **Efficiency:** Drastically reduce the time from selecting a recitation to having a finalized video ready for distribution.
- **Accessibility:** Empower creators of all skill levels to produce visually appealing and accurate Islamic content.
- **Consistency:** Maintain high standards of visual and audio quality across all generated media.

## Key Features
- **Automated Video Assembly:** Intelligent blending of audio recitations with synchronized text translations and background visuals.
- **Word-by-Word Synchronization:** Advanced video generation engine that renders synchronized Arabic words and translations using multi-line segmentation and configurable typography.
    - **Configurable Pacing:** Support for adjustable delays between verses to improve recitation flow.
    - **Enhanced Overlays:** Optional full-ayah translation at the bottom of the screen with configurable database sources and font sizes.
    - **Interlinear Rendering:** New specialized layout that centers translations directly beneath each Arabic word with solid underlines for improved clarity.
    - **Optimized Layout:** Refined positioning of metadata (Reciter, Surah, Brand) and translation overlays for better visibility.
    - **UX Refinements:** Streamlined form submission workflow with intuitive redirects and quick-reset background options.
- **Job Management System:** A robust backend that queues video generation tasks, allowing for bulk processing.
- **Visual Customization:** User-defined themes, including font choices, color palettes, and background styles.
- **Dynamic Background Management:** Integrated stock image search (Unsplash) and local file upload system to customize video backgrounds per-job.
    - **Paginated Discovery:** Enhanced image search with 20 results per page and navigation controls for richer asset discovery.
- **Reciter Management:** Support for detailed reciter metadata, including optional links to word-by-word (WBW) segmentation databases with automated file-existence validation.
- **Media Asset Persistence:** A dedicated database (`media_assets`) to track all generated content, its metadata, and disk locations.
- **YouTube Ecosystem Integration:** 
    - Automatic uploading of new videos based on configuration flags.
    - **Shorts Optimization:** Intelligent duration validation and automatic metadata enhancement (e.g., `#Shorts` tagging) for Shorts-formatted content.
        - **Custom Title Prefixes:** Ability to provide user-defined title segments.
        - **SEO-Optimized Metadata:** Automated generation of SEO-friendly descriptions and relevant YouTube tags.
    - Manual management and upload interface for existing media.
    - **Direct Interface Integration:** Streamlined upload and playlist selection directly from the Word-by-Word generation interface.
    - **Flexible Playlist Management:** Support for "None (Upload Only)" defaults and explicit "Reciter's Default" overrides in the WBW workflow.
    - Integration with YouTube playlists organized by reciter.

## User Experience
The web interface provides a centralized dashboard for managing the entire content lifecycle. It features a specialized "Word-by-Word" creation interface for synchronized content, and users can dynamically select video backgrounds from a searchable Unsplash gallery or upload local files. It also includes an enhanced "Manual Upload" dashboard where users can view generated assets in-browser, manage files with atomic/bulk deletion, and track upload statuses through reciter-grouped collapsible sections.
