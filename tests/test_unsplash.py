import pytest
from unittest.mock import patch, MagicMock
import os
from net_ops.unsplash import search_unsplash, download_unsplash_image

def test_unsplash_module_exists():
    assert search_unsplash is not None
    assert download_unsplash_image is not None

@patch("net_ops.unsplash.UNSPLASH_ACCESS_KEY", "fake_key")
@patch("net_ops.unsplash.requests.get")
def test_search_unsplash(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {"id": "1", "urls": {"thumb": "thumb_url", "full": "full_url"}},
        ]
    }
    mock_get.return_value = mock_response
    
    results = search_unsplash("nature")
    assert len(results) == 1
    assert results[0]["id"] == "1"

@patch("net_ops.unsplash.requests.get")
def test_download_unsplash_image(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"image_content"
    mock_response.iter_content.return_value = [b"image_content"]
    mock_get.return_value = mock_response
    
    with patch("builtins.open", MagicMock()):
        with patch("os.path.exists", return_value=True):
            path = download_unsplash_image("full_url", "test_image.jpg")
            assert "test_image.jpg" in path
