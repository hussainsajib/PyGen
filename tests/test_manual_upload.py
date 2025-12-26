from fastapi.testclient import TestClient
from app import app
from processes.video_utils import discover_assets
import pytest
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_manual_upload_route_exists():
    with patch("app.crud_reciters.get_all_reciters") as mock_reciters:
        mock_reciters.return_value = []
        with patch("app.discover_assets") as mock_discover:
            mock_discover.return_value = []
            response = client.get("/manual-upload")
            assert response.status_code == 200

def test_discover_assets_structure():
    # Test discover_assets with empty reciters to check structure
    assets = discover_assets(reciters=[])
    assert isinstance(assets, list)

def test_manual_upload_grouped_data_logic():
    # Mock reciter data
    mock_reciter = MagicMock()
    mock_reciter.english_name = "Mishary Alafasy"
    mock_reciter.playlist_id = "PL123"
    
    mock_video = {
        "filename": "quran_video_1_Mishary Alafasy.mp4",
        "surah_number": "1",
        "reciter": "Mishary Alafasy",
        "screenshot_present": True,
        "details_present": True,
        "details_filename": "1_1_7_mishary_alafasy.txt",
        "playlist_id": "PL123",
        "playlist_status": "PL123"
    }

    with patch("app.crud_reciters.get_all_reciters") as mock_reciters:
        mock_reciters.return_value = [mock_reciter]
        with patch("app.discover_assets") as mock_discover:
            mock_discover.return_value = [mock_video]
            response = client.get("/manual-upload")
            assert response.status_code == 200
            # Check if grouped reciter name is in the response text
            assert "Mishary Alafasy" in response.text
            assert "PL123" in response.text