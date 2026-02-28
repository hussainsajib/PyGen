from fastapi.testclient import TestClient
from app import app, get_db
import pytest
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_wbw_fast_form_has_correct_hidden_inputs():
    with patch("app.crud_reciters.get_all_reciters") as mock_reciters, patch("app.get_all_languages") as mock_langs:
        mock_reciters.return_value = []
        mock_langs.return_value = []
        
        # Override get_db to prevent real DB calls
        async def override_get_db():
            yield MagicMock()
        app.dependency_overrides[get_db] = override_get_db
        
        response = client.get("/wbw-fast")
        assert response.status_code == 200
        
        html_content = response.content.decode('utf-8')
        assert 'action="/create-video"' in html_content
        assert 'name="job_type" value="wbw"' in html_content
        assert 'name="engine_type" value="ffmpeg"' in html_content
        
        app.dependency_overrides.clear()
