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

def test_trigger_manual_upload_route():
    with patch("app.enqueue_manual_upload_job") as mock_enqueue:
        mock_enqueue.return_value = None
        # Mocking get_all_jobs since Redirect follows to /jobs which calls it
        with patch("app.get_all_jobs") as mock_jobs:
            mock_jobs.return_value = []
            response = client.post("/trigger-manual-upload", data={
                "video_filename": "quran_video_1_Mishary Alafasy.mp4",
                "reciter_key": "ar.alafasy",
                "playlist_id": "PL123",
                "details_filename": "1_1_7_mishary_alafasy.txt"
            }, follow_redirects=True)
            assert response.status_code == 200