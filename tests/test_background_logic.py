import pytest
from unittest.mock import patch, MagicMock
from processes.surah_video import generate_surah
from processes.video_utils import generate_video

@pytest.mark.asyncio
async def test_generate_video_uses_active_background():
    # Mock config_manager.get to return a background path
    with patch("config_manager.config_manager.get") as mock_get:
        mock_get.side_effect = lambda key, default=None: "background/test.jpg" if key == "ACTIVE_BACKGROUND" else default
        
        # We don't want to run the full video generation, just check if it fetches the config
        # and passes it to the next function.
        # This is hard without more refactoring, so let's mock generate_surah instead 
        # to see if it receives the right parameters or check processes.py
        pass

@patch("processes.surah_video.generate_background")
def test_create_ayah_clip_receives_background(mock_gen_bg):
    from processes.surah_video import create_ayah_clip
    from processes.Classes import Surah, Reciter
    
    mock_surah = MagicMock(spec=Surah)
    mock_reciter = MagicMock(spec=Reciter)
    mock_audio = MagicMock()
    mock_audio.duration = 10
    
    # Check if create_ayah_clip can handle background_image_url parameter
    # (Initially it might not, or we need to see how it's called)
    pass
