from fastapi.testclient import TestClient
from app import app
import pytest

@pytest.mark.asyncio
async def test_wbw_responsive_classes():
    with TestClient(app) as client:
        response = client.get("/word-by-word")
        assert response.status_code == 200
        
        # Check for Verse Range responsive classes
        assert 'col-12' in response.text
        assert 'col-md-6' in response.text

@pytest.mark.asyncio
async def test_wbw_tables_responsive():
    with TestClient(app) as client:
        response = client.get("/word-by-word")
        assert response.status_code == 200
        
        if "<table" in response.text:
            assert 'table-responsive' in response.text
