import os
import sys
import asyncio
from PIL import Image
import numpy as np

sys.path.append(os.getcwd())

from db_ops.crud_mushaf import get_mushaf_page_data
from factories.mushaf_fast_render import MushafRenderer
from factories.mushaf_ffmpeg_engine import FFmpegEngine

async def repro_fast():
    # Setup
    page_num = 603
    page_data = get_mushaf_page_data(page_num)
    
    # We only need one page for reproduction
    renderer = MushafRenderer(page_num, is_short=False, lines=page_data)
    renderer.prepare_static_base()
    
    # Check if the text in the renderer matches our expected fixed text
    # The renderer pre-calculates highlight rects using the same logic
    # But we can also just check a frame
    frame = renderer.get_frame_at(0)
    
    # Save the frame
    Image.fromarray(frame).save("repro_fast_110_3.png")
    print("Saved repro_fast_110_3.png")

if __name__ == "__main__":
    asyncio.run(repro_fast())
