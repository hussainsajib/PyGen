import pytest
import os
import numpy as np
from moviepy.editor import AudioFileClip, concatenate_audioclips
from moviepy.audio.AudioClip import AudioArrayClip
import tempfile

def make_dummy_mp3(duration, path):
    fps = 44100
    n_samples = int(duration * fps)
    data = np.zeros((n_samples, 2))
    clip = AudioArrayClip(data, fps=fps)
    clip.write_audiofile(path, fps=fps, logger=None)
    clip.close()

def test_juz_audio_subclip_out_of_bounds():
    """
    Simulates the out-of-bounds error that occurs when end_t is derived from 
    external timestamps and slightly exceeds the actual AudioFileClip duration.
    """
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        temp_path = f.name
    
    try:
        # 1. Create a dummy audio file of 10 seconds
        duration = 10.0
        make_dummy_mp3(duration, temp_path)
        
        # 2. Read it back
        clip = AudioFileClip(temp_path)
        
        # 3. Simulate external timestamps that are slightly off (e.g. 10.05s)
        # In the real bug, these come from the SQLite WBW database
        start_t = 0.0
        end_t = 11.0 # Clearly beyond the 10.03s duration
        
        # This is the logic currently in processes/mushaf_video.py:prepare_juz_data_package
        # It should fail when writing the concatenated result
        subclip = clip.subclip(start_t, end_t)
        
        # We wrap it in a concatenation to mimic the real usage
        full_audio = concatenate_audioclips([subclip])
        
        # Attempting to write this should trigger the out-of-bounds error
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f2:
            out_path = f2.name
        
        # This is expected to raise an Exception
        with pytest.raises(Exception) as excinfo:
            full_audio.write_audiofile(out_path, logger=None)
        
        assert "Accessing time t=" in str(excinfo.value)
        assert "with clip duration=" in str(excinfo.value)
        
        print(f"\nCaught expected error: {excinfo.value}")

    finally:
        if 'clip' in locals(): clip.close()
        if 'full_audio' in locals(): full_audio.close()
        if os.path.exists(temp_path): os.remove(temp_path)
        if 'out_path' in locals() and os.path.exists(out_path): os.remove(out_path)

if __name__ == "__main__":
    test_juz_audio_subclip_out_of_bounds()
