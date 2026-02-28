from fastapi.testclient import TestClient
from app import app, get_db
import pytest
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_wbw_fast_route_exists():
    with patch("app.crud_reciters.get_all_reciters") as mock_reciters, patch("app.get_all_languages") as mock_langs:
        mock_reciters.return_value = []
        mock_langs.return_value = []
        
        # Override get_db to prevent real DB calls
        async def override_get_db():
            yield MagicMock()
        app.dependency_overrides[get_db] = override_get_db
        
        response = client.get("/wbw-fast")
        assert response.status_code == 200
        app.dependency_overrides.clear()

def test_wbw_fast_form_submission():
    with patch("app.enqueue_job") as mock_enqueue:
        # Override get_db
        async def override_get_db():
            yield MagicMock()
        app.dependency_overrides[get_db] = override_get_db
        
        # Assuming the new form submits to /create-video with job_type wbw and engine_type ffmpeg
        response = client.get("/create-video", params={
            "surah": 1,
            "start_verse": 1,
            "end_verse": 7,
            "reciter": "ar.alafasy",
            "job_type": "wbw",
            "engine_type": "ffmpeg"
        }, follow_redirects=False)
        assert response.status_code in [303, 307]
        mock_enqueue.assert_called_once()
        kwargs = mock_enqueue.call_args.kwargs
        assert kwargs.get("job_type") == "wbw"
        assert kwargs.get("engine_type") == "ffmpeg"
        app.dependency_overrides.clear()
