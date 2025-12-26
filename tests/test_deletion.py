import pytest
from unittest.mock import patch, MagicMock, AsyncMock, ANY
from fastapi.testclient import TestClient
from app import app
from db.models import MediaAsset
import os

client = TestClient(app)

@pytest.mark.asyncio
async def test_atomic_deletion_logic():
    mock_asset = MagicMock(spec=MediaAsset)
    mock_asset.id = 1
    mock_asset.video_path = "exported_data/videos/test.mp4"
    mock_asset.screenshot_path = "exported_data/screenshots/test.png"
    mock_asset.details_path = "exported_data/details/test.txt"
    
    with patch("app.crud_media_assets.get_media_asset_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_asset
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            with patch("os.remove") as mock_remove:
                with patch("app.crud_media_assets.delete_media_asset", new_callable=AsyncMock) as mock_delete:
                    # Mock context for redirect
                    with patch("app.crud_media_assets.get_all_media_assets", new_callable=AsyncMock) as mock_get_all:
                        mock_get_all.return_value = []
                        with patch("app.crud_reciters.get_all_reciters", new_callable=AsyncMock) as mock_get_reciters:
                            mock_get_reciters.return_value = []
                            
                            response = client.post("/delete-media/1", follow_redirects=True)
                            assert response.status_code == 200
                            assert mock_remove.call_count == 3
                            mock_delete.assert_called_once_with(ANY, 1)

@pytest.mark.asyncio
async def test_bulk_deletion_logic():
    mock_asset1 = MagicMock(spec=MediaAsset)
    mock_asset1.id = 1
    mock_asset1.video_path = "v1.mp4"
    mock_asset1.screenshot_path = "s1.png"
    mock_asset1.details_path = "d1.txt"
    
    mock_asset2 = MagicMock(spec=MediaAsset)
    mock_asset2.id = 2
    mock_asset2.video_path = "v2.mp4"
    mock_asset2.screenshot_path = "s2.png"
    mock_asset2.details_path = "d2.txt"
    
    with patch("app.crud_media_assets.get_media_asset_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [mock_asset1, mock_asset2]
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            with patch("os.remove") as mock_remove:
                with patch("app.crud_media_assets.delete_media_asset", new_callable=AsyncMock) as mock_delete:
                    with patch("app.crud_media_assets.get_all_media_assets", new_callable=AsyncMock) as mock_get_all:
                        mock_get_all.return_value = []
                        with patch("app.crud_reciters.get_all_reciters", new_callable=AsyncMock) as mock_get_reciters:
                            mock_get_reciters.return_value = []
                            
                            # FastAPI TestClient doesn't automatically parse list of values in data
                            # We might need to use json or multiple entries
                            response = client.post("/delete-bulk-media", data={"asset_ids": [1, 2]}, follow_redirects=True)
                            assert response.status_code == 200
                            assert mock_remove.call_count == 6
                            assert mock_delete.call_count == 2