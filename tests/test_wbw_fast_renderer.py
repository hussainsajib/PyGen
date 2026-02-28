import pytest
from processes.wbw_fast_video import MoviePyRenderer
from moviepy.editor import ColorClip

def test_moviepy_renderer_initialization():
    clip = ColorClip(size=(1280, 720), color=(255, 0, 0), duration=1.0)
    renderer = MoviePyRenderer(clip)
    
    assert renderer.resolution == (1280, 720)
    
    # Render a frame
    frame = renderer.get_frame_at(0.0)
    assert frame is not None
    assert frame.shape == (720, 1280, 3) # height, width, channels

