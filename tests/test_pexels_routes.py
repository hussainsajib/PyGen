from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app
import pytest

client = TestClient(app)

def test_pexels_search_route():
    mock_results = [{"id": 1, "preview": "img.jpg", "video_url": "vid.mp4"}]
    
    with patch("app.search_pexels_videos") as mock_search:
        mock_search.return_value = mock_results
        
        response = client.get("/pexels-search?query=nature&page=1&orientation=landscape")
        
        assert response.status_code == 200
        assert response.json() == mock_results
        mock_search.assert_called_with("nature", page=1, orientation="landscape")

def test_download_pexels_video_route():
    with patch("app.download_file") as mock_download:
        mock_download.return_value = "background/video.mp4"
        
        response = client.post("/download-pexels-video", data={"url": "http://example.com/vid.mp4", "filename": "vid.mp4"})
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["path"] == "background/video.mp4"
