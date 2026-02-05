# Specification: Mushaf Video Generation Optimization (Static Flattening)

## Overview
This track implements critical performance optimizations for the Mushaf video generation engine, specifically targeting long-form "Juz" videos. Following the findings in `bottlenecks.md`, we will shift from a multi-layered real-time compositing approach to a "Static Flattening" model. This reduces the number of active MoviePy layers from 17+ down to 2-3 per frame, significantly cutting down generation time.

## Goals
- Reduce Juz video generation time from ~26 hours to a target of < 5 hours.
- Implement pre-compositing of static page elements into a single image.
- Introduce font object caching to reduce I/O overhead in text rendering.
- Add Ayah-range selection within Juz generation for efficient testing.

## Functional Requirements

### 1. Engine Optimization: Static Layer Flattening
- **Pre-rendering Logic:** Modify `generate_mushaf_page_clip` in `factories/single_clip.py` to:
    - Create a single RGBA canvas the size of the video resolution.
    - Draw the background, border, Surah header, Basmallah, and all Ayah text lines for the chunk onto this single canvas using Pillow.
    - Use this single pre-rendered image as the primary `ImageClip` layer.
- **Dynamic Layering:** Highlighting (ColorClips) and progress bars will remain as separate layers on top of the flattened base to maintain their dynamic nature.

### 2. Rendering Optimization: Font Caching
- **Font Cache:** Implement a global LRU or simple dictionary cache for `ImageFont` objects in `factories/single_clip.py`.
- **Performance:** Ensure `render_mushaf_text_to_image` reuses cached font objects instead of reloading `.ttf` files for every line.

### 3. Testing Enhancement: Range Selection
- **Optional Range:** Update `generate_juz_video` to accept optional `start_ayah` and `end_ayah` parameters.
- **Selective Generation:** If a range is provided, the engine will only process pages and Surahs within that specific segment of the Juz.

## Non-Functional Requirements
- **Visual Fidelity:** The flattened output must be visually identical to the multi-layered output.
- **Memory Management:** Ensure the pre-rendering process does not cause memory leaks during long Juz runs.

## Acceptance Criteria
- [ ] Full Juz video generation speed improves by at least 5x based on benchmarking Surah 108 or a small Juz segment.
- [ ] A Juz generation run can be restricted to a specific Ayah range (e.g., Juz 1, Surah 2, Ayahs 1-10) for testing.
- [ ] Visual inspection confirms that borders, text alignment, and highlighting remain correct.
- [ ] `bottlenecks.md` is updated with the new performance metrics.

## Out of Scope
- Migrating to a different rendering engine (e.g., Manim).
- Implementing GPU-accelerated encoding.
