import pytest
from fastapi.testclient import TestClient
from app import app
import os
import io

client = TestClient(app)

def test_upload_background_endpoint_exists():
    # This will fail with 404 until implemented
    response = client.post("/upload-background")
    assert response.status_code != 404

def test_upload_background_success():
    background_dir = "background"
    if not os.path.exists(background_dir):
        os.makedirs(background_dir)
        
    file_content = b"fake image content"
    file_name = "test_bg.jpg"
    
    response = client.post(
        "/upload-background",
        files={"file": (file_name, io.BytesIO(file_content), "image/jpeg")}
    )
    
    assert response.status_code == 200
    assert response.json()["filename"] == file_name
    assert os.path.exists(os.path.join(background_dir, file_name))
    
    # Cleanup
    os.remove(os.path.join(background_dir, file_name))
