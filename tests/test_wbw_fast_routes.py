from fastapi.testclient import TestClient
from app import app
import pytest
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_wbw_fast_route_exists():
    with patch("db_ops.crud_reciters.get_all_reciters") as mock_reciters:
        mock_reciters.return_value = []
        response = client.get("/wbw-fast")
        assert response.status_code == 200

def test_wbw_fast_form_submission():
    with patch("app.enqueue_job") as mock_enqueue:
        # Assuming the new form submits to /create-video with job_type wbw and engine_type ffmpeg
        response = client.get("/create-video", params={
            "surah": 1,
            "start_verse": 1,
            "end_verse": 7,
            "reciter": "ar.alafasy",
            "job_type": "wbw",
            "engine_type": "ffmpeg"
        })
        assert response.status_code == 303
        mock_enqueue.assert_called_once()
        kwargs = mock_enqueue.call_args.kwargs
        assert kwargs.get("job_type") == "wbw"
        assert kwargs.get("engine_type") == "ffmpeg"
