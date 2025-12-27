from fastapi.testclient import TestClient
from app import app
from config_manager import config_manager
from db.database import async_session
import pytest
import asyncio

@pytest.mark.asyncio
async def test_config_ui_settings():
    # Force reload of config once to pick up all new entries
    async with async_session() as session:
        await config_manager.load_from_db(session, reload=True)
        
    client = TestClient(app)
    response = client.get("/config")
    assert response.status_code == 200
    
    # Check for Delay setting
    assert "WBW_DELAY_BETWEEN_AYAH" in response.text
    
    # Check for Full Translation settings
    assert "WBW_FULL_TRANSLATION_ENABLED" in response.text
    assert "WBW_FULL_TRANSLATION_SOURCE" in response.text