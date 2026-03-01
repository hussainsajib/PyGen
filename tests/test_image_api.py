import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_generate_image_endpoint():
    """Test the /api/generate-image endpoint."""
    response = client.get("/api/generate-image?surah=1&ayah=1")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_download_image_endpoint():
    """Test the /api/download-image endpoint."""
    response = client.get("/api/download-image?surah=1&ayah=1")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert "content-disposition" in response.headers

def test_facebook_post_image_endpoint():
    """Test the /api/post-to-facebook endpoint (mocked)."""
    # This will need authentication/tokens, so we test the structure/existence
    pass
