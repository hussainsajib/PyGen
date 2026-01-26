from factories.single_clip import generate_mushaf_page_clip
from moviepy.editor import ColorClip, CompositeVideoClip
import os
import sys

# Add project root to path for local imports if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

mock_lines = [
    {
        "line_number": 1,
        "words": [{"text": "ﱁﱂﱃ"}],
        "start_ms": 0,
        "end_ms": 1000
    },
    {
        "line_number": 2,
        "words": [{"text": "ﱄﱅﱆ"}],
        "start_ms": 1000,
        "end_ms": 2000
    }
]

# Note: This uses Page 1 font (p1.ttf) if available in QPC_V2_Font.ttf/
clip = generate_mushaf_page_clip(mock_lines, page_number=1, is_short=False, duration=2.5)

# Overlay on a dark background to make it visible
bg = ColorClip(size=clip.size, color=(20, 20, 20)).set_duration(2.5)
final = CompositeVideoClip([bg, clip])

output_path = "test_mushaf_rendering.mp4"
print(f"Generating verification video: {output_path}")
final.write_videofile(output_path, fps=24)
print(f"Done. Please check {output_path} in the root directory.")
