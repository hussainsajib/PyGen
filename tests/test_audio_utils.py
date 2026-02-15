import pytest
import os
import numpy as np
from factories.video import make_silence, get_standard_basmallah_clip
from moviepy.editor import AudioFileClip

def test_make_silence():
    duration = 1.0
    silence = make_silence(duration)
    assert silence.duration == duration
    # Check if frame is silence (zeros)
    frame = silence.get_frame(0.5)
    assert np.all(frame == 0)

def test_get_standard_basmallah_clip():
    # This assumes the file exists in the test environment or is mocked
    # For now, let's just check if it returns an AudioFileClip-like object
    # if the file exists.
    basmalah_path = "recitation_data/basmalah.mp3"
    if os.path.exists(basmalah_path):
        clip = get_standard_basmallah_clip()
        assert clip is not None
        assert clip.duration > 0
        clip.close()
    else:
        with pytest.raises(FileNotFoundError):
            get_standard_basmallah_clip()
