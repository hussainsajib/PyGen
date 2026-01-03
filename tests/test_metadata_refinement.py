import pytest
from unittest.mock import MagicMock, patch
import os
from processes.description import generate_video_title

@pytest.fixture
def mock_surah():
    surah = MagicMock()
    surah.number = 2
    surah.english_name = "Al-Baqarah"
    surah.bangla_name = "আল-বাকারা"
    return surah

@pytest.fixture
def mock_reciter():
    reciter = MagicMock()
    reciter.english_name = "Mishary Al-Afasy"
    reciter.bangla_name = "মিশারি আল-আফাসি"
    return reciter

def test_generate_video_title_bengali_single(mock_surah, mock_reciter, tmp_path):
    filename = tmp_path / "test_title.txt"
    generate_video_title(mock_surah, mock_reciter, True, str(filename), is_short=True, start=1, end=1, language="bengali")
    
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read().strip()
    
    # Expected: ২. সুরাহ আল-বাকারা (১) - মিশারি আল-আফাসি
    assert content == "২. সুরাহ আল-বাকারা (১) - মিশারি আল-আফাসি"

def test_generate_video_title_bengali_range(mock_surah, mock_reciter, tmp_path):
    filename = tmp_path / "test_title.txt"
    generate_video_title(mock_surah, mock_reciter, True, str(filename), is_short=True, start=1, end=5, language="bengali")
    
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read().strip()
    
    # Expected: ২. সুরাহ আল-বাকারা (১-৫) - মিশারি আল-আফাসি
    assert content == "২. সুরাহ আল-বাকারা (১-৫) - মিশারি আল-আফাসি"

def test_generate_video_title_english_single(mock_surah, mock_reciter, tmp_path):
    filename = tmp_path / "test_title.txt"
    generate_video_title(mock_surah, mock_reciter, True, str(filename), is_short=True, start=1, end=1, language="english")
    
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read().strip()
    
    # Expected: 2. Surah Al-Baqarah (1) - Mishary Al-Afasy
    assert content == "2. Surah Al-Baqarah (1) - Mishary Al-Afasy"

def test_generate_video_title_english_range(mock_surah, mock_reciter, tmp_path):
    filename = tmp_path / "test_title.txt"
    generate_video_title(mock_surah, mock_reciter, True, str(filename), is_short=True, start=1, end=5, language="english")
    
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read().strip()
    
    # Expected: 2. Surah Al-Baqarah (1-5) - Mishary Al-Afasy
    assert content == "2. Surah Al-Baqarah (1-5) - Mishary Al-Afasy"

def test_generate_video_description_bengali(mock_surah, mock_reciter, tmp_path):
    filename = tmp_path / "test_desc.txt"
    # Note: in real usage, title is already written. For this test we just check the description part.
    from processes.description import generate_video_description
    generate_video_description(mock_surah, mock_reciter, str(filename), is_short=True, start=1, end=5, language="bengali")
    
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check for title info in header
    assert "২. সুরাহ আল-বাকারা (১-৫) - মিশারি আল-আফাসি" in content
    # Check for custom message
    assert "কুরআনের এই সুন্দর তিলাওয়াতটি শুনুন এবং শেয়ার করুন।" in content
    # Check for social links
    assert "https://www.facebook.com/profile.php?id=61570927757129" in content
    # Check for handle
    assert "@TaqwaBangla" in content
    # Check for tags
    assert "TAGS:" in content
    assert "Taqwa Bangla" in content
    assert "Shorts" in content

def test_generate_details_full_content(mock_surah, mock_reciter, tmp_path):
    from processes.description import generate_details
    # Mock the directory structure
    details_dir = tmp_path / "exported_data" / "details"
    details_dir.mkdir(parents=True)
    
    with patch("processes.description.os.path.isfile", return_value=False):
        with patch("processes.description.os.remove"):
            # We need to change the hardcoded path in the function for testing or just mock the open
            # Given the function hardcodes 'exported_data/details/', we'll use a patch on 'open'
            with patch("processes.description.open", create=True) as mock_open:
                # Setup mock file to capture writes
                from io import StringIO
                written_data = StringIO()
                mock_file = MagicMock()
                mock_file.write.side_effect = lambda s: written_data.write(s)
                mock_open.return_value.__enter__.return_value = mock_file
                
                generate_details(mock_surah, mock_reciter, True, 1, 5, is_short=True, language="bengali")
                
                full_content = written_data.getvalue()
                
                # Verify structure
                lines = full_content.strip().split("\n")
                # Line 1: YouTube Title
                assert lines[0] == "২. সুরাহ আল-বাকারা (১-৫) - মিশারি আল-আফাসি"
                # Description header (after \n\n)
                assert "২. সুরাহ আল-বাকারা (১-৫) - মিশারি আল-আফাসি" in full_content
                # Social Links
                assert "https://www.facebook.com/profile.php?id=61570927757129" in full_content
                # Hashtags
                assert "#Shorts" in full_content
                assert "#TaqwaBangla" in full_content
                # Tags line
                assert "TAGS:" in full_content
                assert "Taqwa Bangla" in full_content
