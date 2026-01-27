
import asyncio
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.models.config import Config

class ConfigManager:
    """
    A singleton class to manage application configuration.
    It loads configuration from the database once and provides an in-memory cache.
    """
    _instance = None
    _config: List[Dict[str, Any]] = [] # Changed to List of Dicts
    _overrides: Dict[str, Any] = {} # New: Local overrides
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def set_local_override(self, key: str, value: Any):
        """Sets a temporary local override for a config key."""
        self._overrides[key] = value

    def clear_local_overrides(self):
        """Clears all local overrides."""
        self._overrides = {}

    async def load_from_db(self, db_session: AsyncSession, reload: bool = False):
        """Loads all configuration key-value pairs from the database."""
        async with self._lock:
            # Check if config is already loaded (or if we need to reload due to changes)
            if not self._config or reload: 
                print("Loading configuration from database...")
                stmt = select(Config).order_by(Config.id) # Order by ID here
                result = await db_session.execute(stmt)
                all_config_items = result.scalars().all()
                # Store as list of dicts including ID
                self._config = [{"id": item.id, "key": item.key, "value": item.value} for item in all_config_items]
                print(f"Configuration loaded with {len(self._config)} items.")

    def get_all(self) -> List[Dict[str, Any]]: # Changed return type
        """Returns a copy of the entire configuration cache, sorted by ID."""
        # Already sorted from load_from_db, but re-sorting here for safety/consistency if items were added/modified
        return sorted(self._config.copy(), key=lambda item: item['id'])

    def get(self, key: str, default: Any = None) -> Any:
        """Gets a value from the configuration cache, respecting local overrides."""
        if key in self._overrides:
            return self._overrides[key]
            
        for item in self._config:
            if item["key"] == key:
                return item["value"]
        return default

    async def set(self, db_session: AsyncSession, key: str, value: Any):
        """Sets a value in the cache and persists it to the database."""
        # Check DB first to ensure consistency
        stmt = select(Config).where(Config.key == key)
        result = await db_session.execute(stmt)
        existing_db_item = result.scalars().first()

        if existing_db_item:
            # Update existing
            existing_db_item.value = value
            await db_session.commit()
            
            # Update cache
            found_in_cache = False
            for item in self._config:
                if item["key"] == key:
                    item["value"] = value
                    found_in_cache = True
                    break
            
            if not found_in_cache:
                self._config.append({"id": existing_db_item.id, "key": existing_db_item.key, "value": existing_db_item.value})
                self._config.sort(key=lambda item: item['id'])
        
        else: # Not in DB, Insert
            new_db_item = Config(key=key, value=value)
            db_session.add(new_db_item)
            await db_session.commit()
            await db_session.refresh(new_db_item) # Refresh to get ID
            
            # Add to cache and keep sorted
            self._config.append({"id": new_db_item.id, "key": new_db_item.key, "value": new_db_item.value})
            self._config.sort(key=lambda item: item['id']) # Re-sort cache
        

    async def delete(self, db_session: AsyncSession, key: str):
        """Deletes a key from the cache and the database."""
        # Remove from cache
        self._config = [item for item in self._config if item["key"] != key]
        self._config.sort(key=lambda item: item['id']) # Re-sort cache

        # Remove from database
        stmt = select(Config).where(Config.key == key)
        result = await db_session.execute(stmt)
        db_config_item = result.scalars().first()

        if db_config_item:
            await db_session.delete(db_config_item)
            await db_session.commit()

# Singleton instance
config_manager = ConfigManager()

def get_config_manager() -> ConfigManager:
    """FastAPI dependency to get the config manager instance."""
    return config_manager
