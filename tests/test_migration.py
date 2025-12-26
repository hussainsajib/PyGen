import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import os
from scripts.migrate_media import scan_and_map_assets

@pytest.mark.asyncio
async def test_scan_and_map_logic():
    mock_session = AsyncMock()
    # Mock crud_reciters.get_all_reciters
    with patch("db_ops.crud_reciters.get_all_reciters", new_callable=AsyncMock) as mock_get_reciters:
        mock_reciter = MagicMock()
        mock_reciter.english_name = "Mishary Alafasy"
        mock_reciter.reciter_key = "ar.alafasy"
        mock_get_reciters.return_value = [mock_reciter]
        
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            with patch("os.listdir") as mock_listdir:
                # Simulate one video file
                mock_listdir.side_effect = lambda path: {
                    "exported_data/videos": ["quran_video_1_Mishary Alafasy.mp4"],
                    "exported_data/screenshots": ["screenshot_quran_video_1_Mishary Alafasy.png"],
                    "exported_data/details": ["1_1_7_mishary_alafasy.txt"]
                }.get(path, [])
                
                with patch("os.path.getsize") as mock_getsize:
                    mock_getsize.return_value = 1024 * 1024 # 1MB
                    
                    assets = await scan_and_map_assets(mock_session)
                    
                    assert len(assets) == 1
                    assert assets[0]["surah_number"] == 1
                    assert assets[0]["reciter_key"] == "ar.alafasy"
                    assert assets[0]["start_ayah"] == 1
                    assert assets[0]["end_ayah"] == 7