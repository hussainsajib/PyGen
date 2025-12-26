import pytest
from db.models.reciter import Reciter

def test_reciter_has_wbw_database_field():
    reciter = Reciter(
        reciter_key="test_key",
        english_name="Test Reciter",
        bangla_name="টেস্ট ক্বারী",
        wbw_database="test_wbw.db"
    )
    assert reciter.wbw_database == "test_wbw.db"
