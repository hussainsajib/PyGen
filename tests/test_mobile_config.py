from fastapi.testclient import TestClient
from app import app
import pytest

@pytest.mark.asyncio
async def test_config_tables_responsive():
    with TestClient(app) as client:
        response = client.get("/config")
        assert response.status_code == 200
        
        # Check if tables are wrapped in table-responsive
        # We search for '<div class="table-responsive"><table'
        assert 'table-responsive' in response.text

@pytest.mark.asyncio
async def test_config_form_responsive():
    with TestClient(app) as client:
        response = client.get("/config")
        assert response.status_code == 200
        
        # Check if the "Create New Config" form uses responsive grid
        assert 'col-12' in response.text
        assert 'col-md-auto' in response.text or 'col-md' in response.text
