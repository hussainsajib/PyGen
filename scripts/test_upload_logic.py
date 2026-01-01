import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from processes.processes import _get_target_youtube_channel_id
from config_manager import config_manager
from db.database import async_session

async def test_logic():
    async with async_session() as session:
        await config_manager.load_from_db(session)
        
        # Test Bengali
        print("Testing Bengali channel ID retrieval...")
        await config_manager.set(session, "DEFAULT_LANGUAGE", "bengali")
        bn_id = await _get_target_youtube_channel_id()
        print(f"Bengali Channel ID: {bn_id}")
        assert bn_id == "UCVfyI5zQRcJxuJMxreY6I8g"
        
        # Test English
        print("Testing English channel ID retrieval...")
        await config_manager.set(session, "DEFAULT_LANGUAGE", "english")
        en_id = await _get_target_youtube_channel_id()
        print(f"English Channel ID: {en_id}")
        assert en_id == "UC-TtqbMYI3TzOxfyEqT8VGQ"
        
        print("Tests passed!")

if __name__ == "__main__":
    asyncio.run(test_logic())
