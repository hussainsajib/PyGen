import pytest
from fastapi.testclient import TestClient
from app import app
import os

client = TestClient(app)

def test_mushaf_route_page_param():
    """Verify that the /mushaf endpoint accepts a page parameter."""
    response = client.get("/mushaf?page=10")
    assert response.status_code == 200
    assert "Page 10" in response.text

def test_static_font_serving():
    """Verify that font files are accessible via the static route."""
    # We expect fonts to be served at /mushaf-fonts/p1.ttf
    response = client.get("/mushaf-fonts/p1.ttf")
    assert response.status_code == 200
    # Content-type can vary by OS/environment, but usually it's font-related or octet-stream or text/plain
    assert response.headers["content-type"] in ["font/ttf", "application/x-font-ttf", "application/octet-stream", "text/plain; charset=utf-8"]
