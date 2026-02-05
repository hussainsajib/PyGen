import pytest
from unittest.mock import patch, MagicMock
from db_ops.crud_mushaf import get_ayahs_for_page_range

def test_get_ayahs_for_page_range_success():
    """
    Test that get_ayahs_for_page_range returns correct surah/ayah boundaries for a page range.
    """
    with patch('sqlite3.connect') as mock_connect:
        # Mocking two database connections: DB_15_LINES and DB_WBW
        mock_conn_15line = MagicMock()
        mock_conn_wbw = MagicMock()
        mock_connect.side_effect = [mock_conn_15line, mock_conn_wbw]
        
        # Mock cursor for 15line DB
        mock_cursor_15line = mock_conn_15line.cursor.return_value
        # Page 1: first_word_id=1, Page 2: last_word_id=100
        mock_cursor_15line.fetchone.return_value = (1, 100)
        
        # Mock cursor for WBW DB
        mock_cursor_wbw = mock_conn_wbw.cursor.return_value
        # Start word (ID 1): Surah 1, Ayah 1
        # End word (ID 100): Surah 2, Ayah 5
        mock_cursor_wbw.fetchone.side_effect = [(1, 1), (2, 5)]
        
        result = get_ayahs_for_page_range(1, 2)
        
        assert result == {
            "start_surah": 1,
            "start_ayah": 1,
            "end_surah": 2,
            "end_ayah": 5
        }
        
        # Verify queries
        mock_cursor_15line.execute.assert_called_once()
        assert "MIN(first_word_id), MAX(last_word_id)" in mock_cursor_15line.execute.call_args[0][0]
        
        assert mock_cursor_wbw.execute.call_count == 2
        # Check if it queries for IDs 1 and 100
        calls = mock_cursor_wbw.execute.call_args_list
        assert calls[0][0][1] == (1,)
        assert calls[1][0][1] == (100,)

def test_get_ayahs_for_page_range_invalid_range():
    """
    Test that it returns None if the range yields no words.
    """
    with patch('sqlite3.connect') as mock_connect:
        mock_conn_15line = MagicMock()
        mock_connect.return_value = mock_conn_15line
        mock_cursor_15line = mock_conn_15line.cursor.return_value
        mock_cursor_15line.fetchone.return_value = (None, None)
        
        result = get_ayahs_for_page_range(999, 1000)
        assert result is None
