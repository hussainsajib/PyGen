import pytest
from unittest.mock import MagicMock, patch
# We will create this module next
from scripts.mushaf_mapper import get_page_content

def test_get_page_content_success():
    """Test retrieving and mapping page content."""
    mock_conn_15line = MagicMock()
    mock_cursor_15line = MagicMock()
    mock_conn_wbw = MagicMock()
    mock_cursor_wbw = MagicMock()
    
    # Mock data for Page 1 (Surah Fatiha)
    mock_cursor_15line.fetchall.return_value = [
        (1, 1, 'bismillah', 1, 1, 4, 1),
        (1, 2, 'ayah', 1, 5, 8, 1)
    ]
    
    def side_effect_wbw_execute(query, params):
        if "words" in query:
            start, end = params
            if start == 1 and end == 4:
                mock_cursor_wbw.fetchall.return_value = [
                    (1, "1:1:1", 1, 1, 1, "Bismi"),
                    (2, "1:1:2", 1, 1, 2, "Allahi"),
                    (3, "1:1:3", 1, 1, 3, "Ar-Rahmani"),
                    (4, "1:1:4", 1, 1, 4, "Ar-Raheem")
                ]
            elif start == 5 and end == 8:
                mock_cursor_wbw.fetchall.return_value = [
                    (5, "1:2:1", 1, 2, 1, "Al-Hamdu"),
                    (6, "1:2:2", 1, 2, 2, "Lillahi"),
                    (7, "1:2:3", 1, 2, 3, "Rabbi"),
                    (8, "1:2:4", 1, 2, 4, "Al-Alameen")
                ]
        return mock_cursor_wbw

    mock_cursor_wbw.execute.side_effect = side_effect_wbw_execute
    
    mock_conn_15line.cursor.return_value = mock_cursor_15line
    mock_conn_wbw.cursor.return_value = mock_cursor_wbw
    
    # Mock the connections
    with patch('scripts.mushaf_mapper.sqlite3.connect') as mock_connect:
        def side_effect_connect(db_path):
            if "15-lines" in db_path:
                return mock_conn_15line
            else:
                return mock_conn_wbw
        mock_connect.side_effect = side_effect_connect
        
        result = get_page_content(1, "path/to/15-lines.db", "path/to/wbw.db")
        
        assert len(result) == 2 # 2 lines
        assert result[0]['line_number'] == 1
        assert len(result[0]['words']) == 4
        assert result[0]['words'][0]['text'] == "Bismi"
        
        assert result[1]['line_number'] == 2
        assert len(result[1]['words']) == 4
        assert result[1]['words'][0]['text'] == "Al-Hamdu"