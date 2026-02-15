import pytest
import os
from factories.mushaf_ffmpeg_engine import FFmpegEngine
from factories.mushaf_fast_render import MushafRenderer

@pytest.mark.asyncio
async def test_ffmpeg_engine_instantiation():
    renderer = MushafRenderer(1, True, [])
    engine = FFmpegEngine(renderer, "output.mp4")
    assert engine.renderer == renderer
    assert engine.output_path == "output.mp4"

@pytest.mark.asyncio
async def test_ffmpeg_engine_render_loop():
    # This will be a light test using a mock/small duration
    lines = [{
        "line_type": "ayah",
        "words": [{"text": "test"}],
        "start_ms": 0,
        "end_ms": 100
    }]
    renderer = MushafRenderer(1, True, lines)
    output_path = "test_ffmpeg_output.mp4"
    engine = FFmpegEngine(renderer, output_path)
    
    # Render 0.2 seconds of video
    await engine.generate(duration_sec=0.2, audio_path=None)
    
    assert os.path.exists(output_path)
    # Clean up
    if os.path.exists(output_path):
        os.remove(output_path)
