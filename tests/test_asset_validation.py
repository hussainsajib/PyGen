import pytest
from unittest.mock import patch, MagicMock
import os

def test_validate_mushaf_assets_missing_fonts():
    """
    Test that validate_mushaf_assets returns a list of missing font files.
    """
    from processes.mushaf_video import validate_mushaf_assets
    
    # Mock os.path.exists to return False for some fonts
    with patch('os.path.exists') as mock_exists:
        # Suppose we need page 1, 2, and headers
        # We'll make p2.ttf and BSML missing
        def side_effect(path):
            if "p2.ttf" in path or "QCF_BSML.TTF" in path:
                return False
            return True
        mock_exists.side_effect = side_effect
        
        missing = validate_mushaf_assets(page_numbers=[1, 2])
        
        assert len(missing) == 2
        assert any("p2.ttf" in m for m in missing)
        assert any("QCF_BSML.TTF" in m for m in missing)

def test_validate_mushaf_assets_all_present():
    """
    Test that it returns an empty list if all assets are present.
    """
    from processes.mushaf_video import validate_mushaf_assets
    
    with patch('os.path.exists', return_value=True):
        missing = validate_mushaf_assets(page_numbers=[1, 2, 3])
        assert len(missing) == 0
