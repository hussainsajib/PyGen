import pytest
from unittest.mock import patch, MagicMock
from db_ops.crud_mushaf import get_mushaf_page_data_structured

def test_get_mushaf_page_data_structured_ayah_concatenation():
    """Test that words in an ayah line are correctly concatenated."""
    mock_lines = [
        (1, 1, 'ayah', 0, 1, 3, 1) # page, line, type, centered, start_id, end_id, surah
    ]
    mock_words = [
        ('word1',),
        ('word2',),
        ('word3',)
    ]
    
    with patch('sqlite3.connect') as mock_connect:
        mock_conn_15 = mock_connect.return_value
        mock_cursor_15 = mock_conn_15.cursor.return_value
        mock_cursor_15.fetchall.return_value = mock_lines
        
        # Second call to connect for WBW DB
        mock_conn_wbw = MagicMock()
        mock_connect.side_effect = [mock_conn_15, mock_conn_wbw]
        mock_cursor_wbw = mock_conn_wbw.cursor.return_value
        mock_cursor_wbw.fetchall.return_value = mock_words
        
        result = get_mushaf_page_data_structured(1)
        
        assert len(result) == 1
        assert result[0]['line_type'] == 'ayah'
        assert result[0]['text'] == 'word1 word2 word3'
        assert result[0]['is_centered'] is False

def test_get_mushaf_page_data_structured_metadata_fields():
    """Test that surah_name and basmallah fields are correctly returned."""
    mock_lines = [
        (1, 1, 'surah_name', 1, None, None, 1),
        (1, 2, 'basmallah', 1, None, None, 1)
    ]
    
    with patch('sqlite3.connect') as mock_connect:
        mock_conn_15 = mock_connect.return_value
        mock_cursor_15 = mock_conn_15.cursor.return_value
        mock_cursor_15.fetchall.return_value = mock_lines
        
        mock_conn_wbw = MagicMock()
        mock_connect.side_effect = [mock_conn_15, mock_conn_wbw]
        
        result = get_mushaf_page_data_structured(1)
        
        assert len(result) == 2
        assert result[0]['line_type'] == 'surah_name'
        assert result[0]['surah_number'] == 1
        assert result[0]['is_centered'] is True
        assert result[1]['line_type'] == 'basmallah'
        assert result[1]['is_centered'] is True
