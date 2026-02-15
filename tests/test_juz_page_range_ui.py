import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
from app import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_create_juz_video_with_range_params():
    """Verify that the create-juz-video route accepts and passes page range params."""
    with patch("app.enqueue_job", new_callable=AsyncMock) as mock_enqueue, \
         patch("app.get_db"), \
         patch("app.get_config_manager"), \
         patch("app.get_all_jobs", return_value=[]):
        
        # We use follow_redirects=False to catch the 303
        response = client.get("/create-juz-video?juz=1&reciter=ar.alafasy&start_page=2&end_page=3", follow_redirects=False)
        
        assert response.status_code == 303 # Redirects to /jobs
        mock_enqueue.assert_called_once()
        args, kwargs = mock_enqueue.call_args
        assert kwargs["start_page"] == 2
        assert kwargs["end_page"] == 3
        assert kwargs["surah_number"] == 1
        assert kwargs["job_type"] == "juz_video"

def test_juz_video_ui_has_range_inputs():
    """Verify that the Juz Video interface template renders the new range inputs."""
    # We need to mock database dependencies for the interface GET request
    with patch("db_ops.crud_reciters.get_all_reciters", new_callable=AsyncMock) as mock_reciters, \
         patch("db_ops.crud_language.get_all_languages", new_callable=AsyncMock) as mock_langs:
        
        mock_reciters.return_value = []
        mock_langs.return_value = []
        
        response = client.get("/juz-video")
        assert response.status_code == 200
        assert 'name="start_page"' in response.text
        assert 'name="end_page"' in response.text
        assert 'onsubmit="return validateForm()"' in response.text