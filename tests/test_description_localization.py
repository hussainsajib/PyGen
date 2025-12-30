import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from processes.description import generate_details
from db.models.language import Language
from db.models.reciter import Reciter
from db.models.surah import Surah

@pytest.fixture
def mock_surah_obj():
    mock_surah = MagicMock(spec=Surah)
    mock_surah.number = 1
    mock_surah.english_name = "Al-Fatiha"
    mock_surah.bangla_name = "আল-ফাতিহা"
    return mock_surah

@pytest.fixture
def mock_reciter_obj():
    mock_reciter = MagicMock(spec=Reciter)
    mock_reciter.english_name = "Abdul Basit"
    mock_reciter.bangla_name = "আব্দুল বাসিত"
    return mock_reciter

def test_generate_details_english(mock_surah_obj, mock_reciter_obj):
    # Mock open to capture file content
    mock_file_content = {}
    
    def mock_open(filename, mode, encoding):
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.write.side_effect = lambda x: mock_file_content.update({filename: mock_file_content.get(filename, '') + x})
        return mock_file

    with patch("builtins.open", side_effect=mock_open), \
         patch("json.dump"), \
         patch("processes.description.os.path.exists", return_value=False), \
         patch("processes.description.os.makedirs"):
        
        # Test English output
        details_path = generate_details(
            mock_surah_obj,
            mock_reciter_obj,
            has_translation=True,
            start=1,
            end=7,
            is_short=False,
            custom_title=None,
            language="english"
        )
        
        expected_filename = f"exported_data/details/{mock_surah_obj.number}_{1}_{7}_{mock_reciter_obj.english_name.lower().replace(' ', '_')}.txt"
        assert details_path == expected_filename

        # Assertions for content
        content = mock_file_content.get(expected_filename, '')
        assert f"{mock_surah_obj.english_name} - {mock_reciter_obj.english_name} - with English Translation" in content # Title line
        assert f"Surah {mock_surah_obj.english_name}\nRecited by: {mock_reciter_obj.english_name}" in content # Description lines
        assert "TAGS: Quran, Islam, Islamic, Quran Tilawat, Abdul Basit, Al-Fatiha, Taqwa" in content


def test_generate_details_bengali(mock_surah_obj, mock_reciter_obj):
    # Mock open to capture file content
    mock_file_content = {}
    
    def mock_open(filename, mode, encoding):
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.write.side_effect = lambda x: mock_file_content.update({filename: mock_file_content.get(filename, '') + x})
        return mock_file

    with patch("builtins.open", side_effect=mock_open), \
         patch("json.dump"), \
         patch("processes.description.os.path.exists", return_value=False), \
         patch("processes.description.os.makedirs"):
        
        # Test Bengali output
        details_path = generate_details(
            mock_surah_obj,
            mock_reciter_obj,
            has_translation=True,
            start=1,
            end=7,
            is_short=False,
            custom_title=None,
            language="bengali"
        )
        
        expected_filename = f"exported_data/details/{mock_surah_obj.number}_{1}_{7}_{mock_reciter_obj.english_name.lower().replace(' ', '_')}.txt"
        assert details_path == expected_filename

        # Assertions for content
        content = mock_file_content.get(expected_filename, '')
        assert f"১ - {mock_surah_obj.bangla_name} - {mock_reciter_obj.bangla_name} - বাংলা অনুবাদসহ" in content # Title line
        assert f"সুরাহ {mock_surah_obj.bangla_name}\nতিলাওয়াতঃ {mock_reciter_obj.bangla_name}" in content # Description lines
        assert "TAGS: Quran, Islam, Islamic, Quran Tilawat, আব্দুল বাসিত, আল-ফাতিহা, Takwa Bangla" in content