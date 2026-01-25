from config_manager import config_manager
from db.database import async_session
import pytest

@pytest.mark.asyncio
async def test_config_manager_set_update():
    key = "UNIT_TEST_KEY"
    value = "val1"
    
    async with async_session() as session:
        # 1. Set new
        await config_manager.set(session, key, value)
        assert config_manager.get(key) == value
        
        # 2. Update existing
        new_value = "val2"
        await config_manager.set(session, key, new_value)
        assert config_manager.get(key) == new_value
        
        # 3. Cleanup
        await config_manager.delete(session, key)
        assert config_manager.get(key) is None

@pytest.mark.asyncio
async def test_config_manager_set_missing_cache():
    # Test the case where DB has it but cache doesn't
    key = "UNIT_TEST_KEY_2"
    value = "val1"
    
    async with async_session() as session:
        await config_manager.set(session, key, value)
    
    # Manually remove from cache to simulate missing cache
    config_manager._config = [item for item in config_manager._config if item['key'] != key]
    assert config_manager.get(key) is None
    
    async with async_session() as session:
        # Update should find it in DB and update cache
        new_value = "val2"
        await config_manager.set(session, key, new_value)
        
        assert config_manager.get(key) == new_value
        
        # Cleanup
        await config_manager.delete(session, key)
