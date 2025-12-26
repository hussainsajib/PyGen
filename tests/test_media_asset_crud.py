import pytest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from db_ops import crud_media_assets
from db.models.media_asset import MediaAsset

@pytest.mark.asyncio
async def test_get_all_media_assets():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result
    
    assets = await crud_media_assets.get_all_media_assets(mock_session)
    assert assets == []

@pytest.mark.asyncio
async def test_delete_media_asset():
    mock_session = AsyncMock(spec=AsyncSession)
    
    # Mock get_media_asset_by_id return
    mock_asset = MagicMock(spec=MediaAsset)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_asset
    mock_session.execute.return_value = mock_result
    
    result = await crud_media_assets.delete_media_asset(mock_session, 1)
    assert result is True
    mock_session.delete.assert_called_once_with(mock_asset)
