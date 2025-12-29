import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.base import Base
from db.models.language import Language
from db_ops.crud_language import get_all_languages
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_get_all_languages():
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the result of the query
    mock_result = MagicMock()
    mock_language = Language(name="test", code="tst")
    mock_result.scalars.return_value.all.return_value = [mock_language]
    mock_db.execute.return_value = mock_result
    
    languages = await get_all_languages(mock_db)
    
    assert len(languages) == 1
    assert languages[0].name == "test"
    mock_db.execute.assert_called_once()
