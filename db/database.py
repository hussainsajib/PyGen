import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from db.models import Base  # this auto-imports all models due to __init__.py

DATABASE_URL = "sqlite+aiosqlite:///./jobs.db"
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with async_session() as session:
        yield session
