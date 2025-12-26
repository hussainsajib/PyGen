from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from db.models.media_asset import MediaAsset

async def create_media_asset(session: AsyncSession, asset_data: dict):
    asset = MediaAsset(**asset_data)
    session.add(asset)
    await session.commit()
    await session.refresh(asset)
    return asset

async def get_all_media_assets(session: AsyncSession):
    result = await session.execute(select(MediaAsset).order_by(MediaAsset.created_at.desc()))
    return result.scalars().all()

async def get_media_asset_by_id(session: AsyncSession, asset_id: int):
    result = await session.execute(select(MediaAsset).where(MediaAsset.id == asset_id))
    return result.scalar_one_or_none()

async def update_media_asset(session: AsyncSession, asset_id: int, asset_data: dict):
    asset = await get_media_asset_by_id(session, asset_id)
    if asset:
        for key, value in asset_data.items():
            setattr(asset, key, value)
        await session.commit()
        await session.refresh(asset)
    return asset

async def delete_media_asset(session: AsyncSession, asset_id: int):
    asset = await get_media_asset_by_id(session, asset_id)
    if asset:
        await session.delete(asset)
        await session.commit()
        return True
    return False

async def delete_bulk_media_assets(session: AsyncSession, asset_ids: list[int]):
    # Note: This doesn't handle disk deletion, which will be in Phase 4
    await session.execute(delete(MediaAsset).where(MediaAsset.id.in_(asset_ids)))
    await session.commit()
    return True
