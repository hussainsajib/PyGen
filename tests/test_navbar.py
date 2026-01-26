import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_mushaf_link_in_navbar():
    """Verify that the Mushaf link is present in the navigation bar on the home page."""
    response = client.get("/")
    assert response.status_code == 200
    # Check for the link in the HTML
    # TestClient might prepend http://testserver
    assert '/mushaf' in response.text
    assert "Mushaf" in response.text
