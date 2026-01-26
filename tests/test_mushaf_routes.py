from fastapi.testclient import TestClient
from app import app
import pytest
from unittest.mock import patch, MagicMock, mock_open
import json

client = TestClient(app)

def test_create_mushaf_video_route_redirects():
    """Test that the route enqueues a job and redirects to /jobs."""
    mock_surah_data = {
        "1": {"english_name": "Al-Fatihah"}
    }
    
    # Patch enqueue_job in app module
    with patch("app.enqueue_job") as mock_enqueue, \
         patch("app.get_db") as mock_db, \
         patch("app.get_config_manager") as mock_config, \
         patch("builtins.open", mock_open(read_data=json.dumps(mock_surah_data))):
        
        # Mock enqueue_job to be async
        mock_enqueue.return_value = MagicMock()
        
        response = client.get("/create-mushaf-video?surah=1&reciter=ar.alafasy&lines_per_page=8", follow_redirects=False)
        
        # Should redirect to /jobs (303 RedirectResponse)
        assert response.status_code == 303
        assert response.headers["location"] == "/jobs"
        
        # Check if enqueue_job was called with correct type
        mock_enqueue.assert_called_once()
        kwargs = mock_enqueue.call_args.kwargs
        assert kwargs["job_type"] == "mushaf_video"
        assert kwargs["surah_number"] == 1
        assert kwargs["reciter"] == "ar.alafasy"
        assert kwargs["lines_per_page"] == 8
