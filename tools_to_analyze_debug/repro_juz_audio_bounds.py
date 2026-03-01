import os
import numpy as np
import tempfile
from moviepy.editor import AudioFileClip, concatenate_audioclips
from moviepy.audio.AudioClip import AudioArrayClip

def reproduce_fixed():
    print("Starting reproduction with FIX (clamping)...")
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        temp_path = f.name
        
    duration = 46.0
    fps = 44100
    n_samples = int(duration * fps)
    data = np.zeros((n_samples, 2))
    clip = AudioArrayClip(data, fps=fps)
    clip.write_audiofile(temp_path, fps=fps, logger=None)
    
    print(f"Created temp MP3: {temp_path}, duration={duration}")
    
    # Now read it back as AudioFileClip
    afc = AudioFileClip(temp_path)
    print(f"Read back duration: {afc.duration}")
    
    # Simulated problematic timestamp
    start_t = 45.0
    end_t = 46.53 
    
    # APPLY FIX (as done in processes/mushaf_video.py)
    clamped_end_t = min(afc.duration - 0.001, end_t)
    
    print(f"Attempting subclip: start={start_t}, end={clamped_end_t} (Clamped from {end_t})")
    
    try:
        sub = afc.subclip(start_t, clamped_end_t)
        print(f"Subclip duration: {sub.duration}")
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f2:
            sub_path = f2.name
        
        sub.write_audiofile(sub_path, fps=fps, logger=None)
        print("\n[SUCCESS] Write successful with clamping fix!")
    except Exception as e:
        print(f"\n[FAILURE] Still caught error with fix: {e}")
    finally:
        afc.close()
        if 'sub' in locals(): sub.close()
        if os.path.exists(temp_path): os.remove(temp_path)
        if 'sub_path' in locals() and os.path.exists(sub_path):
            try: os.remove(sub_path)
            except: pass

if __name__ == "__main__":
    reproduce_fixed()
