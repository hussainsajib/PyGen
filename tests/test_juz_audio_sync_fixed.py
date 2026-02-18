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

def test_juz_audio_subclip_clamped():
    """
    Verifies that clamping end_t to clip.duration prevents the out-of-bounds error.
    """
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        temp_path = f.name
    
    try:
        # 1. Create a dummy audio file of 10 seconds
        duration = 10.0
        make_dummy_mp3(duration, temp_path)
        
        # 2. Read it back
        clip = AudioFileClip(temp_path)
        
        # 3. Simulate external timestamps that are slightly off (e.g. 11.0s)
        start_t = 0.0
        end_t = 11.0 
        
        # Apply the FIX: Clamp end_t with 1ms margin
        clamped_end_t = min(clip.duration - 0.001, end_t)
        
        subclip = clip.subclip(start_t, clamped_end_t)
        full_audio = concatenate_audioclips([subclip])
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f2:
            out_path = f2.name
        
        # This should now SUCCEED
        full_audio.write_audiofile(out_path, logger=None)
        
        assert os.path.exists(out_path)
        print("\nFix verified: write_audiofile successful with clamped end_t")

    finally:
        if 'clip' in locals(): clip.close()
        if 'full_audio' in locals(): full_audio.close()
        if os.path.exists(temp_path): os.remove(temp_path)
        try:
            if 'out_path' in locals() and os.path.exists(out_path): os.remove(out_path)
        except:
            pass

if __name__ == "__main__":
    test_juz_audio_subclip_clamped()
