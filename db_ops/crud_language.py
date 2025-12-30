from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.language import Language
from db.models.reciter import Reciter
from db.models.surah import Surah
from db.models.language_translation import LanguageTranslation
from config_manager import config_manager
from db_ops.crud_reciters import get_reciter_by_key


async def get_all_languages(db: AsyncSession):
    result = await db.execute(select(Language))
    return result.scalars().all()

async def get_translations_for_language(db: AsyncSession, language_id: int):
    """Fetches all translation databases for a given language."""
    result = await db.execute(select(LanguageTranslation).where(LanguageTranslation.language_id == language_id))
    return result.scalars().all()

async def fetch_localized_metadata(session: AsyncSession, surah_number: int, reciter_tag: str, config_manager_obj):
    """Fetches localized metadata (reciter, font, brand_name, surah) from DB."""
    reciter_obj = await get_reciter_by_key(session, reciter_tag)
    
    lang_name = config_manager_obj.get("DEFAULT_LANGUAGE", "bengali")
    result_lang = await session.execute(select(Language).filter_by(name=lang_name))
    lang_obj = result_lang.scalar_one_or_none()
    
    language_font = lang_obj.font if lang_obj else "arial.ttf"
    brand_name = lang_obj.brand_name if lang_obj and lang_obj.brand_name else "Taqwa"

    result_surah = await session.execute(select(Surah).filter_by(number=surah_number))
    surah_obj = result_surah.scalar_one_or_none()
    
    return reciter_obj, lang_obj, surah_obj