from fastapi.testclient import TestClient
from app import app
from config_manager import config_manager
from db.database import async_session
import pytest

@pytest.mark.asyncio
async def test_wbw_page_config_controls_present():
    client = TestClient(app)
    response = client.get("/word-by-word")
    assert response.status_code == 200
    
    # Check for Language dropdown
    assert 'id="default_language_select"' in response.text
    
    # Check for Upload switches
    assert 'id="upload_to_youtube_checkbox"' in response.text
    assert 'id="enable_facebook_upload_checkbox"' in response.text

@pytest.mark.asyncio
async def test_wbw_page_config_initialization():
    # Set specific config values
    async with async_session() as session:
        await config_manager.set(session, "UPLOAD_TO_YOUTUBE", "True")
        await config_manager.set(session, "ENABLE_FACEBOOK_UPLOAD", "False")
        await config_manager.set(session, "DEFAULT_LANGUAGE", "english")
    
    client = TestClient(app)
    response = client.get("/word-by-word")
    
    # Check if initialized correctly
    # YouTube should be checked
    assert 'id="upload_to_youtube_checkbox" checked' in response.text or 'id="upload_to_youtube_checkbox"  checked' in response.text
    
    # Facebook should NOT be checked
    assert 'id="enable_facebook_upload_checkbox" checked' not in response.text
    
    # Language should have english selected
    assert '<option value="english" selected>' in response.text
