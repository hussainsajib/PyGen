import pytest
import os
from factories.mushaf_opencv_engine import OpenCVEngine
from factories.mushaf_fast_render import MushafRenderer

@pytest.mark.asyncio
async def test_opencv_engine_instantiation():
    renderer = MushafRenderer(1, True, [])
    engine = OpenCVEngine(renderer, "output_cv.mp4")
    assert engine.renderer == renderer
    assert engine.output_path == "output_cv.mp4"

@pytest.mark.asyncio
async def test_opencv_engine_render_loop():
    lines = [{
        "line_type": "ayah",
        "words": [{"text": "test"}],
        "start_ms": 0,
        "end_ms": 100
    }]
    renderer = MushafRenderer(1, True, lines)
    output_path = "test_opencv_output.mp4"
    engine = OpenCVEngine(renderer, output_path)
    
    # Render 0.2 seconds of video
    await engine.generate(duration_sec=0.2, audio_path=None)
    
    assert os.path.exists(output_path)
    # Clean up
    if os.path.exists(output_path):
        os.remove(output_path)
