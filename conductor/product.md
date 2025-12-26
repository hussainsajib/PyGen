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
- **Job Management System:** A robust backend that queues video generation tasks, allowing for bulk processing.
- **Visual Customization:** User-defined themes, including font choices, color palettes, and background styles.
- **YouTube Ecosystem Integration:** 
    - Automatic uploading of new videos based on configuration flags.
    - Manual management and upload interface for existing media.
    - Integration with YouTube playlists organized by reciter.

## User Experience
The web interface provides a centralized dashboard for managing the entire content lifecycle: from the initial configuration of a surah and reciter to tracking the final upload status on YouTube.
