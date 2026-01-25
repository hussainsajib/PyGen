from fastapi.testclient import TestClient
from unittest.mock import patch
from app import app
import pytest

client = TestClient(app)

def test_youtube_refresh_route():
    with patch("app.refresh_channel_token") as mock_refresh:
        mock_refresh.return_value = None  # Simulate successful run
        
        response = client.post("/youtube/refresh-token", data={"language_id": 1})
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_refresh.assert_called_once()
