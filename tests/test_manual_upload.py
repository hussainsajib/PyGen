from fastapi.testclient import TestClient
from app import app
from processes.video_utils import discover_assets
import os

client = TestClient(app)

def test_manual_upload_route_exists():
    response = client.get("/manual-upload")
    assert response.status_code == 200

def test_discover_assets():

    assets = discover_assets()

    assert isinstance(assets, list)

    if len(assets) > 0:

        asset = assets[0]

        assert "filename" in asset

        assert "surah_number" in asset

        assert "reciter" in asset

        assert "screenshot_present" in asset

        assert "details_present" in asset
