# Mushaf Video Generation Performance Investigation Report

## Executive Summary
The Mushaf video generation engine currently experiences significant latency, with a performance ratio of approximately **28x** for standard videos (616s for a 22s video). This investigation has identified that the primary bottleneck is not text rendering or I/O, but rather the **MoviePy frame rendering process**, specifically the overhead of flattening multi-layered `CompositeVideoClip`s for every single frame during the `write_videofile` phase.

## Profiling Results

### 1. Text Rendering (Pillow)
- **Status:** Not a bottleneck.
- **Metrics:** ~0.01s per line at font size 150.
- **Analysis:** Pillow rendering is highly efficient.

### 2. Page Assembly (`CompositeVideoClip` Creation)
- **Status:** Not a bottleneck.
- **Metrics:** ~0.08s for a full 15-line page clip.
- **Analysis:** Creating the MoviePy objects in memory is fast.

### 3. Video Encoding (`write_videofile`)
- **Status:** **CRITICAL BOTTLENECK**.
- **Metrics:** 
    - Solid Background: ~3.2x performance ratio (32s for 10s video).
    - Video Background: ~6.4x performance ratio (64s for 10s video).
    - Full Mushaf Video (Surah 108): ~28x performance ratio (616s for 22s video).
- **Analysis:** MoviePy re-renders and flattens every layer (background, border, 15+ text lines) for every single frame. This is mathematically expensive and redundant for mostly static content.

## Identified Bottlenecks

1.  **Redundant Layer Flattening:** MoviePy does not cache the result of flattening static layers. Every frame re-calculates the transparency and positioning of the border, background, and static text lines.
2.  **Video Background Decoding Overhead:** Using an MP3/MP4 background doubles the encoding time because MoviePy must decode the background frame-by-frame and then composite it.
3.  **Lack of Pre-Rendering:** The current architecture renders each line as an individual clip. A page with 15 lines results in 15+ layers that MoviePy must manage throughout the video writing process.

## Recommendations

### Short-Term (High Impact, Low Effort)
1.  **Static Layer Flattening:** Instead of a `CompositeVideoClip` with 17+ layers, pre-render the "static" parts of a page (background + border + surah name + basmallah + all ayah lines) into a single full-page `ImageClip` or `ColorClip`. Then, only layer the "dynamic" parts (like highlighters) on top.
2.  **Font Object Caching:** While small (~7% impact), caching `ImageFont` objects will provide a minor speed boost to the `render_mushaf_text_to_image` function.

### Mid-Term (Medium Impact, Medium Effort)
1.  **Chunking Optimization:** Instead of passing 15 lines to `CompositeVideoClip`, merge all text lines for a specific page/chunk into a single transparent image first, then use that one image as a single MoviePy layer.
2.  **Optimize Highlight Rendering:** Currently, highlights are individual `ColorClip` objects. Consider drawing them directly onto the text images if they are static within a scene.

### Long-Term (Strategic Shift)
1.  **Alternative Rendering Engine:** Evaluate `Manim` or direct `FFmpeg` filtergraphs for composition. FFmpeg's `overlay` filter is significantly more optimized than MoviePy's Python-based flattening.
2.  **GPU Acceleration:** Explore using `h264_nvenc` or `h264_vaapi` codecs if hardware supports it, though the bottleneck is currently CPU-bound rendering, not just encoding.

## Conclusion
The path to speeding up Mushaf video generation lies in **reducing the number of layers** managed by MoviePy. By pre-compositing static elements into single image clips before the `write_videofile` phase, we can expect a significant (potentially 5x-10x) improvement in generation speed.
