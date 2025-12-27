from fastapi.testclient import TestClient
from app import app
from config_manager import config_manager
from db.database import async_session
import pytest
import asyncio

@pytest.mark.asyncio
async def test_config_ui_has_delay():
    # Force reload of config to pick up the new entry
    async with async_session() as session:
        await config_manager.load_from_db(session, reload=True)
        
    client = TestClient(app)
    response = client.get("/config")
    assert response.status_code == 200
    assert "WBW_DELAY_BETWEEN_AYAH" in response.text