import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
from app import app

client = TestClient(app)

@pytest.fixture
def mock_db_deps():
    """Mock database and language dependencies for navbar testing."""
    with patch("db_ops.crud_reciters.get_all_reciters", new_callable=AsyncMock) as mock_reciters, \
         patch("db_ops.crud_language.get_all_languages", new_callable=AsyncMock) as mock_langs:
        
        mock_reciters.return_value = [
            MagicMock(english_name="Mishary Alafasy", reciter_key="ar.alafasy", wbw_database="wbw", playlist_id="PL1")
        ]
        mock_langs.return_value = [
            MagicMock(name="english")
        ]
        yield

def test_juz_mushaf_link_exists(mock_db_deps):
    """Verify that the Juz Mushaf link is present in the navbar."""
    response = client.get("/")
    assert response.status_code == 200
    # Match both absolute and relative paths
    assert 'href="http://testserver/juz-video"' in response.text or 'href="/juz-video"' in response.text
    assert "Juz Mushaf" in response.text

def test_juz_mushaf_active_class(mock_db_deps):
    """Verify that the active class is applied to the Juz Mushaf link on its page."""
    response = client.get("/juz-video")
    assert response.status_code == 200
    # Match active class with either absolute or relative path
    assert 'nav-link active" href="http://testserver/juz-video"' in response.text or \
           'nav-link active" href="/juz-video"' in response.text
