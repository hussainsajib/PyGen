import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient
from app import app
from db.database import get_db
from config_manager import get_config_manager

# Mock dependencies
async def override_get_db():
    mock_db = AsyncMock()
    return mock_db

def override_get_config_manager():
    mock_config = MagicMock()
    mock_config.get_all.return_value = [{"key": "DEFAULT_LANGUAGE", "value": "bengali"}]
    return mock_config

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_config_manager] = override_get_config_manager

client = TestClient(app)

@patch("app.get_all_languages")
def test_config_route_includes_languages(mock_get_languages):
    # Setup mock return value
    mock_lang1 = MagicMock()
    mock_lang1.name = "bengali"
    mock_lang2 = MagicMock()
    mock_lang2.name = "english"
    mock_get_languages.return_value = [mock_lang1, mock_lang2]

    # Make request
    response = client.get("/config")

    # Verify
    assert response.status_code == 200
    assert "bengali" in response.text
    assert "english" in response.text
    # Check for dropdown presence
    assert '<select name="DEFAULT_LANGUAGE"' in response.text
