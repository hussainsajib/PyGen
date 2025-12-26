import pytest
import sqlite3
import os
import json
from db_ops.crud_wbw import get_wbw_timestamps

def test_get_wbw_timestamps_logic():
    # Create a temporary mock database
    db_path = "tests/mock_wbw.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE segments (surah_number INTEGER, ayah_number INTEGER, segments TEXT)")
    # Sample data with some noise (length 1 segments) to test filtering
    mock_segments = [[1, 0, 500], [1], [2, 500, 1000]]
    cursor.execute("INSERT INTO segments VALUES (1, 1, ?)", (json.dumps(mock_segments),))
    conn.commit()
    conn.close()
    
    try:
        timestamps = get_wbw_timestamps(db_path, 1, 1, 1)
        assert len(timestamps) == 1
        assert 1 in timestamps
        assert len(timestamps[1]) == 2 # Only valid segments
        assert timestamps[1][0] == [1, 0, 500]
        assert timestamps[1][1] == [2, 500, 1000]
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)

def test_get_wbw_timestamps_missing_file():
    assert get_wbw_timestamps("non_existent.db", 1, 1, 1) == {}