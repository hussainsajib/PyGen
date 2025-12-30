import pytest
from unittest.mock import patch, MagicMock, AsyncMock, ANY
from processes.surah_video import generate_surah
from db.models.language import Language
from db.models.reciter import Reciter
from db.models.surah import Surah

@pytest.fixture
def mock_db_session_factory():
    """Returns a factory for mock AsyncSessions."""
    with patch("db.database.async_session") as mock_session_cls:
        def _factory():
            mock_session = AsyncMock()
            mock_session_cls.return_value.__aenter__.return_value = mock_session
            return mock_session
        yield _factory

@pytest.fixture
def mock_config_manager():
    with patch("processes.surah_video.config_manager") as mock_config:
        yield mock_config

@pytest.mark.asyncio
async def test_generate_surah_passes_localized_brand_name(mock_db_session_factory, mock_config_manager):
    # Mock data for Language, Reciter, and Surah
    mock_lang_english = MagicMock(spec=Language)
    mock_lang_english.name = "english"
    mock_lang_english.font = "Arial"
    mock_lang_english.brand_name = "Taqwa English"

    mock_lang_bengali = MagicMock(spec=Language)
    mock_lang_bengali.name = "bengali"
    mock_lang_bengali.font = "Kalpurush"
    mock_lang_bengali.brand_name = "তাকওয়া বাংলা"
    
    mock_reciter_obj = MagicMock(spec=Reciter)
    mock_reciter_obj.reciter_key = "test_reciter"
    mock_reciter_obj.database_name = "test_db"
    mock_reciter_obj.english_name = "Test Reciter English"
    mock_reciter_obj.bangla_name = "টেস্ট ক্বারী বাংলা"
    mock_reciter_obj.wbw_database = None # Not a WBW reciter for this test

    mock_surah_obj = MagicMock(spec=Surah)
    mock_surah_obj.number = 1
    mock_surah_obj.english_name = "Al-Fatiha English"
    mock_surah_obj.bangla_name = "আল-ফাতিহা বাংলা"
    mock_surah_obj.total_ayah = 7

    # Mock all external dependencies to prevent actual file ops or video generation
    with patch("processes.surah_video.download_mp3_temp"), \
         patch("processes.surah_video.AudioFileClip"), \
         patch("processes.surah_video.read_surah_data", return_value="http://mock.audio.url"), \
         patch("processes.surah_video.read_text_data"), \
         patch("processes.surah_video.read_translation"), \
         patch("processes.surah_video.read_timestamp_data", return_value=[(1, 1, 0, 1000, "")]), \
         patch("processes.surah_video.get_wbw_timestamps"), \
         patch("processes.surah_video.create_ayah_clip") as mock_create_ayah_clip, \
         patch("processes.surah_video.generate_intro") as mock_generate_intro, \
         patch("processes.surah_video.generate_outro") as mock_generate_outro, \
         patch("processes.surah_video.concatenate_videoclips") as mock_concatenate_videoclips, \
         patch("factories.file.get_filename"), \
         patch("processes.surah_video.generate_details"), \
         patch("db_ops.crud_language.fetch_localized_metadata") as mock_fetch_localized_metadata: # Patch the top-level helper

        mock_clip = MagicMock()
        mock_clip.duration = 1.0
        mock_create_ayah_clip.return_value = mock_clip
        mock_generate_intro.return_value = mock_clip
        mock_generate_outro.return_value = mock_clip
        mock_concatenate_videoclips.return_value = mock_clip

        # --- Test English ---
        mock_fetch_localized_metadata.return_value = (mock_reciter_obj, mock_lang_english.font, mock_lang_english.brand_name, mock_surah_obj, mock_lang_english.name)
        generate_surah(1, "test_reciter")
        
        mock_create_ayah_clip.assert_called_with(ANY, ANY, ANY, ANY, ANY, ANY, ANY, ANY, is_short=ANY, background_image_path=ANY, translation_font=ANY, brand_name=ANY, language="english")
        
        # --- Test Bengali ---
        mock_create_ayah_clip.reset_mock()
        mock_fetch_localized_metadata.return_value = (mock_reciter_obj, mock_lang_bengali.font, mock_lang_bengali.brand_name, mock_surah_obj, mock_lang_bengali.name)
        generate_surah(1, "test_reciter")
        
        mock_create_ayah_clip.assert_called_with(ANY, ANY, ANY, ANY, ANY, ANY, ANY, ANY, is_short=ANY, background_image_path=ANY, translation_font=ANY, brand_name=ANY, language="bengali")
