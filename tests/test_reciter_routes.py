import pytest
from fastapi.testclient import TestClient
from app import app, get_db
from unittest.mock import patch, MagicMock, AsyncMock

client = TestClient(app)

# Dependency override to mock database session
async def override_get_db():
    mock_session = AsyncMock()
    yield mock_session

app.dependency_overrides[get_db] = override_get_db

def test_reciter_create_wbw_validation_fail():
    with patch("app.validate_wbw_exists", return_value=False):
        response = client.post("/reciter/new", data={
            "reciter_key": "test",
            "english_name": "Test",
            "bangla_name": "Test",
            "wbw_database": "non_existent.db"
        }, follow_redirects=False)
        assert response.status_code == 200
        assert "not found in databases/word-by-word/" in response.text

@pytest.mark.asyncio
async def test_reciter_create_wbw_success():
    with patch("app.validate_wbw_exists", return_value=True):
        with patch("db_ops.crud_reciters.create_reciter", new_callable=AsyncMock) as mock_create:
            response = client.post("/reciter/new", data={
                "reciter_key": "test",
                "english_name": "Test",
                "bangla_name": "Test",
                "wbw_database": "exists.db"
            }, follow_redirects=False)
            assert response.status_code == 303
            assert mock_create.call_args[0][1]["wbw_database"] == "exists.db"
