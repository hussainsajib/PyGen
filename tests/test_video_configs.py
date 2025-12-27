import os
import pytest
from unittest.mock import patch
from processes import video_configs

def test_video_encoding_threads_dynamic_calculation():
    # Mock os.cpu_count to return a known value, e.g., 8
    with patch("os.cpu_count", return_value=8):
        # We need to reload the module because constants are calculated at import time
        import importlib
        importlib.reload(video_configs)
        assert video_configs.VIDEO_ENCODING_THREADS == 7

def test_video_encoding_threads_minimum_value():
    # Mock os.cpu_count to return 1 (edge case)
    with patch("os.cpu_count", return_value=1):
        import importlib
        importlib.reload(video_configs)
        assert video_configs.VIDEO_ENCODING_THREADS == 1

def test_video_encoding_threads_fallback_none():
    # Mock os.cpu_count to return None (rare but possible)
    with patch("os.cpu_count", return_value=None):
        import importlib
        importlib.reload(video_configs)
        # Should fallback to a safe default, e.g., 2 or 1
        assert video_configs.VIDEO_ENCODING_THREADS >= 1
