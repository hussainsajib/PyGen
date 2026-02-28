import pytest
import os
import asyncio
from processes.wbw_fast_video import generate_wbw_fast
from db.database import async_session
from db_ops.crud_reciters import get_reciter_by_key

@pytest.mark.asyncio
async def test_generate_wbw_fast_integration():
    surah_number = 1
    start_verse = 1
    end_verse = 7
    reciter_key = "ar.alafasy"
    engine_type = "pillow_opencv" # New engine
    
    # Run generation
    result = await generate_wbw_fast(
        surah_number, start_verse, end_verse, reciter_key, engine_type, is_short=False
    )
    
    assert result is not None
    assert "video" in result
    assert os.path.exists(result["video"])
    assert os.path.getsize(result["video"]) > 0
    
    # Cleanup
    if os.path.exists(result["video"]):
        os.remove(result["video"])
    if os.path.exists(result["info"]):
        os.remove(result["info"])
