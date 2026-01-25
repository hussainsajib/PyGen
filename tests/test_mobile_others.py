from fastapi.testclient import TestClient
from app import app
import pytest

@pytest.mark.asyncio
async def test_reciters_responsive():
    with TestClient(app) as client:
        response = client.get("/reciters")
        assert response.status_code == 200
        assert 'table-responsive' in response.text

@pytest.mark.asyncio
async def test_jobs_responsive():
    with TestClient(app) as client:
        response = client.get("/jobs")
        assert response.status_code == 200
        assert 'table-responsive' in response.text

@pytest.mark.asyncio
async def test_surah_responsive():
    with TestClient(app) as client:
        response = client.get("/surah")
        assert response.status_code == 200
        assert 'col-12 col-md-6' in response.text

@pytest.mark.asyncio
async def test_tafseer_responsive():
    with TestClient(app) as client:
        response = client.get("/tafseer")
        assert response.status_code == 200
        assert 'row' in response.text
        assert 'col-12' in response.text
