
import asyncio
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.models.config import Config

class ConfigManager:
    """
    A singleton class to manage application configuration.
    It loads configuration from the database once and provides an in-memory cache.
    """
    _instance = None
    _config: Dict[str, Any] = {}
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    async def load_from_db(self, db_session: AsyncSession):
        """Loads all configuration key-value pairs from the database."""
        async with self._lock:
            if not self._config:  # Load only if it hasn't been loaded before
                print("Loading configuration from database...")
                stmt = select(Config)
                result = await db_session.execute(stmt)
                all_config_items = result.scalars().all()
                self._config = {item.key: item.value for item in all_config_items}
                print(f"Configuration loaded with {len(self._config)} items.")

    def get_all(self) -> Dict[str, Any]:
        """Returns a copy of the entire configuration cache."""
        return self._config.copy()

    def get(self, key: str, default: Any = None) -> Any:
        """Gets a value from the configuration cache."""
        return self._config.get(key, default)

    async def set(self, db_session: AsyncSession, key: str, value: Any):
        """Sets a value in the cache and persists it to the database."""
        # Update the cache
        self._config[key] = value

        # Persist to database
        stmt = select(Config).where(Config.key == key)
        result = await db_session.execute(stmt)
        db_config_item = result.scalars().first()

        if db_config_item:
            db_config_item.value = value
        else:
            db_config_item = Config(key=key, value=value)
            db_session.add(db_config_item)
        
        await db_session.commit()

# Singleton instance
config_manager = ConfigManager()

def get_config_manager() -> ConfigManager:
    """FastAPI dependency to get the config manager instance."""
    return config_manager
