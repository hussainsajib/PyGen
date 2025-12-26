from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_manual_upload_route_exists():
    response = client.get("/manual-upload")
    assert response.status_code == 200