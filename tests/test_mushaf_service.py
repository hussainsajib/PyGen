import pytest
from unittest.mock import MagicMock, patch
from db_ops.crud_mushaf import get_mushaf_page_data

def test_get_mushaf_page_data_success():
    """Test retrieving mushaf page data with mocked SQLite databases."""
    mock_conn_15line = MagicMock()
    mock_cursor_15line = MagicMock()
    mock_conn_wbw = MagicMock()
    mock_cursor_wbw = MagicMock()
    
    # Mock lines for Page 1
    mock_cursor_15line.fetchall.return_value = [
        (1, 1, 'surah_name', 1, '', '', 1),
        (1, 2, 'ayah', 1, 1, 5, '')
    ]
    
    # Mock words for ID range 1-5
    mock_cursor_wbw.fetchall.return_value = [
        (1, "1:1:1", 1, 1, 1, "ﱁ"),
        (2, "1:1:2", 1, 1, 2, "ﱂ"),
        (3, "1:1:3", 1, 1, 3, "ﱃ"),
        (4, "1:1:4", 1, 1, 4, "ﱄ"),
        (5, "1:1:5", 1, 1, 5, "ﱅ")
    ]
    
    mock_conn_15line.cursor.return_value = mock_cursor_15line
    mock_conn_wbw.cursor.return_value = mock_cursor_wbw
    
    with patch("sqlite3.connect") as mock_connect:
        # Connect returns different mocks based on path
        def side_effect_connect(path):
            if "15-lines" in path: return mock_conn_15line
            return mock_conn_wbw
        mock_connect.side_effect = side_effect_connect
        
        data = get_mushaf_page_data(1)
        
        assert len(data) == 2
        assert data[0]["line_number"] == 1
        assert data[0]["words"] == []
        assert data[1]["line_number"] == 2
        assert len(data[1]["words"]) == 5
        assert data[1]["words"][0]["text"] == "ﱁ"

def test_get_mushaf_page_data_invalid_page():
    """Test behavior with non-existent page."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_conn.cursor.return_value = mock_cursor
    
    with patch("sqlite3.connect", return_value=mock_conn):
        data = get_mushaf_page_data(999)
        assert data == []
