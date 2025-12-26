import pytest
import os
from unittest.mock import patch
from app import validate_wbw_exists

def test_validate_wbw_logic():
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        assert validate_wbw_exists("test.db") is True
        
        mock_exists.return_value = False
        assert validate_wbw_exists("non_existent.db") is False

def test_validate_wbw_optional():
    assert validate_wbw_exists("") is True
    assert validate_wbw_exists(None) is True