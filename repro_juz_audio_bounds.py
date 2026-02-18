import os
import numpy as np
import tempfile
from moviepy.editor import AudioFileClip, concatenate_audioclips
from moviepy.audio.AudioClip import AudioArrayClip

def reproduce():
    print("Starting reproduction with real MP3...")
    
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
    
    # Try to subclip BEYOND the duration, like the Juz logic does
    # Accessing time t=46.48-46.53 seconds, with clip duration=46 seconds
    start_t = 45.0
    end_t = 46.53 
    
    print(f"Attempting subclip: start={start_t}, end={end_t}")
    
    try:
        # MoviePy subclip doesn't fail IMMEDIATELY. 
        # It fails when it tries to READ the frame at that time.
        sub = afc.subclip(start_t, end_t)
        print(f"Subclip duration: {sub.duration}")
        
        # This should fail when it reaches t=46.53
        print("Writing subclip to dummy file...")
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f2:
            sub_path = f2.name
        
        sub.write_audiofile(sub_path, fps=fps, logger=None)
        print("Write successful (unexpected)")
    except Exception as e:
        print(f"Caught expected error during write/read: {e}")
    finally:
        afc.close()
        if 'sub' in locals(): sub.close()
        if os.path.exists(temp_path): os.remove(temp_path)
        if 'sub_path' in locals() and os.path.exists(sub_path): os.remove(sub_path)

if __name__ == "__main__":
    reproduce()
