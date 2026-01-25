import pytest
from unittest.mock import patch, MagicMock
from net_ops.pexels import search_pexels_videos

@pytest.mark.asyncio
@pytest.mark.parametrize("orientation", ["landscape", "portrait", "square", "any", None])
async def test_search_pexels_videos_success(orientation):
    mock_response_data = {
        "videos": [
            {
                "id": 123,
                "image": "thumb.jpg",
                "video_files": [
                    {"quality": "hd", "link": "http://example.com/video.mp4", "width": 1920, "height": 1080}
                ]
            }
        ]
    }
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_response_data)
        
        results = await search_pexels_videos("nature", orientation=orientation)
        
        assert len(results) == 1
        assert results[0]["id"] == 123

        # Check if orientation is correctly passed in params
        _, kwargs = mock_get.call_args
        params = kwargs.get("params", {})
        if orientation and orientation != "any":
            assert params["orientation"] == orientation
        else:
            assert "orientation" not in params

@pytest.mark.asyncio
async def test_search_pexels_videos_failure():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=401) # Unauthorized
        
        results = await search_pexels_videos("nature")
        
        assert results == []
