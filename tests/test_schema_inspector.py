import pytest
import sqlite3
from unittest.mock import patch, MagicMock
# We will create this module in the next step
from scripts.schema_inspector import get_db_schema

def test_get_db_schema_success():
    """Test retrieving schema from a valid sqlite db."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    # Mock tables query result
    mock_cursor.fetchall.side_effect = [
        [('table1',), ('table2',)], # First call: list tables
        [(0, 'id', 'INTEGER', 0, None, 1), (1, 'name', 'TEXT', 0, None, 0)], # Second call: pragma table_info(table1)
        [(0, 'id', 'INTEGER', 0, None, 1), (1, 'value', 'REAL', 0, None, 0)]  # Third call: pragma table_info(table2)
    ]
    
    mock_conn.cursor.return_value = mock_cursor
    
    with patch('sqlite3.connect', return_value=mock_conn) as mock_connect:
        schema = get_db_schema("dummy.db")
        
        mock_connect.assert_called_with("dummy.db")
        assert "table1" in schema
        assert "table2" in schema
        assert schema["table1"][0]["name"] == "id"
        assert schema["table1"][1]["type"] == "TEXT"

def test_get_db_schema_connection_error():
    """Test handling of connection errors."""
    with patch('sqlite3.connect', side_effect=sqlite3.Error("Connection failed")):
        with pytest.raises(sqlite3.Error):
            get_db_schema("bad_path.db")
