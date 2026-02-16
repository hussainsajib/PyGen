# Specification: Configurable Background Dimming & Footer Cleanup

## Overview
This track introduces a configurable background dimming (darkening) effect for Mushaf and Juz Mushaf videos. This effect will be applied to the global video background to enhance the readability of the text overlays. Simultaneously, the existing semi-transparent background bar behind the footer metadata (Reciter, Surah, Brand) will be removed to provide a cleaner visual aesthetic.

## Requirements

### 1. Functional Requirements
- **Configurable Darkness:** Add a new configuration setting `MUSHAF_BACKGROUND_DIMMING` (decimal value 0.0 to 1.0) to control the opacity of a black overlay applied to the global background.
- **Global Application:** The dimming effect must apply to both static image backgrounds and animated video backgrounds.
- **Footer Cleanup:** Remove the semi-transparent background bar currently rendered behind the Reciter Name, Surah Name, and Brand Name in the video footer.
- **Engine Support:** Implement these changes in both the standard MoviePy engine and the high-speed Fast rendering engines.
- **Dashboard Integration:** Expose the new dimming setting in the application's configuration page.

### 2. Technical Requirements
- **Overlay Method:** Use a static semi-transparent black layer (ColorClip in MoviePy, or PIL/OpenCV overlay in Fast engines) positioned behind all content but in front of the background asset.
- **Setting Persistence:** Use `ConfigManager` to manage the new `MUSHAF_BACKGROUND_DIMMING` setting.

## User Interface
- A new input field or slider in the settings page for background darkness.

## Success Criteria
- [ ] Users can adjust the global background darkness from the settings.
- [ ] The footer metadata bar is no longer rendered in any Mushaf video.
- [ ] Footer text remains readable due to the new global dimming effect.
- [ ] The layout is consistent across both standard and high-speed engines.
