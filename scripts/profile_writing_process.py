import os
import time
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from factories.single_clip import generate_mushaf_page_clip
from processes.video_configs import VIDEO_ENCODING_THREADS

def profile_writing():
    print("--- Profiling write_videofile Performance ---")
    
    # Setup a 10-second clip with 15 lines
    lines = []
    for i in range(15):
        lines.append({
            "line_number": i + 1,
            "line_type": "ayah",
            "words": [{"text": "ﱁﱂﱃ"}],
            "start_ms": i * 1000,
            "end_ms": (i + 1) * 1000
        })
        
    duration = 10.0
    page_number = 1
    
    print("Generating page clip...")
    clip = generate_mushaf_page_clip(lines, page_number, is_short=False, duration=duration)
    
    output_path = "benchmark_writing.mp4"
    
    print(f"Starting write_videofile (duration={duration}s, threads={VIDEO_ENCODING_THREADS})...")
    start_time = time.time()
    
    clip.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=VIDEO_ENCODING_THREADS,
        preset="ultrafast",
        logger=None # Disable moviepy's progress bar for cleaner output
    )
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # ... existing code ...
    print(f"\nTotal Writing Time (Solid BG): {total_time:.2f} seconds")
    print(f"Performance Ratio (Solid BG): {total_time / duration:.2f}x")
    
    # Test with Video Background if available
    video_bg_path = "background/2313069.mp4" # Existing file
    if os.path.exists(video_bg_path):
        print(f"\nTesting with Video Background: {video_bg_path}")
        clip_v = generate_mushaf_page_clip(lines, page_number, is_short=False, duration=duration, background_input=video_bg_path)
        start_time = time.time()
        clip_v.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=VIDEO_ENCODING_THREADS,
            preset="ultrafast",
            logger=None
        )
        end_time = time.time()
        total_time_v = end_time - start_time
        print(f"Total Writing Time (Video BG): {total_time_v:.2f} seconds")
        print(f"Performance Ratio (Video BG): {total_time_v / duration:.2f}x")
    
    # Cleanup
    if os.path.exists(output_path):
        os.remove(output_path)

if __name__ == "__main__":
    profile_writing()
