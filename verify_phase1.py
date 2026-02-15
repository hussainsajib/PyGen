import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from factories.video import get_standard_basmallah_clip, make_silence

try:
    clip = get_standard_basmallah_clip()
    print(f"Basmallah duration: {clip.duration}")
    clip.close()

    silence = make_silence(1.0)
    print(f"Silence duration: {silence.duration}")

    print("Manual verification passed.")
except Exception as e:
    print(f"Manual verification failed: {e}")
