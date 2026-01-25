import pytest
from unittest.mock import patch, MagicMock
from processes.video_utils import get_video_duration

def test_get_video_duration_success():
    """Test retrieving duration from a valid video file."""
    mock_clip = MagicMock()
    mock_clip.duration = 45.5
    
    with patch("processes.video_utils.VideoFileClip") as mock_video_file_clip:
        mock_video_file_clip.return_value = mock_clip
        mock_video_file_clip.return_value.__enter__.return_value = mock_clip
        
        duration = get_video_duration("dummy_path.mp4")
        assert duration == 45.5
        mock_video_file_clip.assert_called_once_with("dummy_path.mp4")

def test_get_video_duration_file_not_found():
    """Test behavior when video file does not exist (handled by MoviePy mostly, but we ensure our wrapper handles it)."""
    with patch("processes.video_utils.VideoFileClip", side_effect=IOError("File not found")):
        with pytest.raises(IOError):
            get_video_duration("non_existent.mp4")
