import pytest
import os
import platform
from factories.font_utils import resolve_font_path

def test_resolve_font_path_kalpurush():
    """Verify that Kalpurush can be resolved on Windows (where we know it exists)."""
    if platform.system() != "Windows":
        pytest.skip("This test requires Windows system fonts.")
        
    path = resolve_font_path("Kalpurush")
    assert os.path.isabs(path)
    assert os.path.exists(path)
    assert "kalpurush" in path.lower()

def test_resolve_font_path_fallback():
    """Verify fallback behavior for non-existent font."""
    path = resolve_font_path("NonExistentFont123")
    assert path == "NonExistentFont123"

def test_resolve_font_path_arial():
    """Verify resolution of common system font."""
    if platform.system() == "Windows":
        path = resolve_font_path("Arial")
        assert os.path.isabs(path)
        assert os.path.exists(path)
