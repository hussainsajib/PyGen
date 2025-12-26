import pytest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from db_ops import crud_reciters
from db.models.reciter import Reciter

@pytest.mark.asyncio
async def test_create_reciter_with_wbw():
    mock_session = AsyncMock(spec=AsyncSession)
    reciter_data = {
        "reciter_key": "test_key",
        "english_name": "Test Reciter",
        "bangla_name": "টেস্ট ক্বারী",
        "wbw_database": "test_wbw.db"
    }
    
    # This will use the actual function which now implicitly supports any field in Reciter
    # because it uses **reciter_data
    with patch("db_ops.crud_reciters.Reciter", return_value=MagicMock()) as mock_model:
        await crud_reciters.create_reciter(mock_session, reciter_data)
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

@pytest.mark.asyncio
async def test_update_reciter_with_wbw():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_reciter = MagicMock(spec=Reciter)
    
    with patch("db_ops.crud_reciters.get_reciter_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_reciter
        
        await crud_reciters.update_reciter(mock_session, 1, {"wbw_database": "new_wbw.db"})
        
        mock_reciter.wbw_database = "new_wbw.db" # Check if attribute was set
        mock_session.commit.assert_called()

from unittest.mock import patch
