import pytest
from unittest.mock import MagicMock, patch
from db_ops.crud_mushaf import get_mushaf_page_data

def test_get_mushaf_page_data_structure():
    """Test that get_mushaf_page_data returns the correct structure including line_type."""
    
    mock_conn_15line = MagicMock()
    mock_cursor_15line = MagicMock()
    mock_conn_wbw = MagicMock()
    mock_cursor_wbw = MagicMock()
    
    # Mock return values for pages table
    # page_number, line_number, line_type, is_centered, first_word_id, last_word_id, surah_number
    mock_cursor_15line.fetchall.return_value = [
        (1, 1, 'basmallah', 1, '', '', 1),
        (1, 2, 'surah_name', 1, '', '', 1),
        (1, 3, 'ayah', 0, 1, 5, 1)
    ]
    
    # Mock return values for words table
    # id, location, surah, ayah, word, text
    mock_cursor_wbw.fetchall.return_value = [
        (1, '1:1:1', 1, 1, 1, 'Word1'),
        (5, '1:1:5', 1, 1, 5, 'Word5')
    ]
    
    mock_conn_15line.cursor.return_value = mock_cursor_15line
    mock_conn_wbw.cursor.return_value = mock_cursor_wbw
    
    with patch("sqlite3.connect") as mock_connect:
        def side_effect(db_path):
            if "15-lines" in db_path:
                return mock_conn_15line
            return mock_conn_wbw
        mock_connect.side_effect = side_effect
        
        data = get_mushaf_page_data(1)
        
        assert len(data) == 3
        
        # Check Basmallah Line
        assert data[0]["line_number"] == 1
        assert data[0]["line_type"] == "basmallah"
        assert data[0]["words"] == [] # Should be empty as IDs were empty
        
        # Check Surah Name Line
        assert data[1]["line_number"] == 2
        assert data[1]["line_type"] == "surah_name"
        assert data[1]["words"] == []
        
        # Check Ayah Line
        assert data[2]["line_number"] == 3
        assert data[2]["line_type"] == "ayah"
        assert len(data[2]["words"]) == 2
        assert data[2]["words"][0]["text"] == "Word1"
