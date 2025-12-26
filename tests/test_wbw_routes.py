from fastapi.testclient import TestClient
from app import app
import pytest
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_wbw_route_exists():
    with patch("db_ops.crud_reciters.get_all_reciters") as mock_reciters:
        mock_reciters.return_value = []
        response = client.get("/word-by-word")
        assert response.status_code == 200
