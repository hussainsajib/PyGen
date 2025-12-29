import pytest
from unittest.mock import MagicMock, patch
import os
from db_ops.crud_text import get_full_translation_for_ayah

# Mock config_manager
@pytest.fixture
def mock_config():
    with patch("db_ops.crud_text.config_manager") as mock:
        yield mock

def test_get_full_translation_path_resolution_bengali(mock_config):
    mock_config.get.return_value = "bengali"
    
    # We patch sqlite3.connect so we can check the path passed to it
    with patch("sqlite3.connect") as mock_connect:
        # Mock cursor and result
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ["Test Translation"]
        
        get_full_translation_for_ayah(1, 1, "rawai_al_bayan")
        
        # Check that it tried to connect to the bengali path
        # Since os.path.exists checks might fail in test env if files don't exist, logic might fallback.
        # However, in this environment, the file DOES exist at ./databases/translation/bengali/rawai_al_bayan.sqlite
        # So we expect it to use that path.
        
        expected_path = "./databases/translation/bengali/rawai_al_bayan.sqlite"
        mock_connect.assert_called_with(expected_path)

def test_get_full_translation_path_resolution_english_fallback(mock_config):
    # If we request english, but file doesn't exist, it should fallback (based on my implementation)
    # But wait, my implementation of fallback was:
    # if not os.path.exists(db_path): ... fallback to default/legacy ...
    
    mock_config.get.return_value = "english"
    
    with patch("sqlite3.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ["Test"]
        
        # Mock os.path.exists to return False for English path and True for fallback
        with patch("os.path.exists") as mock_exists:
            def side_effect(path):
                if "english" in path: return False
                if path == "rawai_al_bayan": return False
                if path == "databases/translation/rawai_al_bayan.sqlite": return False
                return True
            mock_exists.side_effect = side_effect
            
            get_full_translation_for_ayah(1, 1, "rawai_al_bayan")
            
            # Should have fallen back to bengali (default hardcoded in my fallback logic)
            expected_fallback = "./databases/translation/bengali/rawai_al_bayan.sqlite"
            mock_connect.assert_called_with(expected_fallback)
