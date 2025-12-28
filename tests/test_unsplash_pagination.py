import pytest
from unittest.mock import patch, MagicMock
from net_ops.unsplash import search_unsplash

@patch("net_ops.unsplash.UNSPLASH_ACCESS_KEY", "fake_key")
@patch("net_ops.unsplash.requests.get")
def test_search_unsplash_with_pagination(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": []}
    mock_get.return_value = mock_response
    
    # Test with custom page and per_page
    search_unsplash("nature", page=2, per_page=20)
    
    # Verify that the API was called with the correct parameters
    args, kwargs = mock_get.call_args
    params = kwargs.get("params", {})
    assert params.get("page") == 2
    assert params.get("per_page") == 20

@patch("app.search_unsplash")
def test_unsplash_search_route_pagination(mock_search):
    from fastapi.testclient import TestClient
    from app import app
    
    mock_search.return_value = []
    client = TestClient(app)
    
    # Call the route with a page parameter
    client.get("/unsplash-search?query=nature&page=3")
    
    # Verify that search_unsplash was called with the correct page
    # Since it's called via run_in_threadpool, we might need to be careful with mocks
    # but run_in_threadpool usually executes synchronously in tests or we can mock it
    mock_search.assert_called_once()
    args, kwargs = mock_search.call_args
    # First arg is query, second is page, third is per_page? 
    # Actually current route is def unsplash_search(query: str):
    # We want it to be def unsplash_search(query: str, page: int = 1):
    assert args[0] == "nature"
    # Check if page was passed (as second positional or keyword)
    if len(args) > 1:
        assert args[1] == 3
    else:
        assert kwargs.get("page") == 3
