import unittest
from unittest.mock import MagicMock
import os
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

from processes.description import generate_juz_details
from processes.Classes import Reciter, Surah

class TestJuzMetadata(unittest.TestCase):
    def setUp(self):
        # Mock Reciter
        self.reciter = MagicMock(spec=Reciter)
        self.reciter.english_name = "Saud Al-Shuraym"
        self.reciter.bangla_name = "সাউদ আল-শুরাইম"
        
        # Mock Surah numbers and names
        # Surah 67 (Al-Mulk) starts Juz 29, then 68 (Al-Qalam)
        self.offsets = {
            67: 5000,   # 5s
            68: 65000   # 1m 5s
        }

    def test_bengali_metadata_format(self):
        """
        Verify the Bengali title and chapter labels follow the new pattern.
        Expected Title: পারা ২৯ - সাউদ আল-শুরাইম - কুরআন তিলাওয়াত
        Expected Chapters: 00:05 সুরা আল-মুলক
        """
        filename = generate_juz_details(
            juz_number=29, 
            reciter=self.reciter, 
            offsets=self.offsets, 
            language="bengali"
        )
        
        with open(filename, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            
        # 1. Title Verification (Should fail - currently 'কুরআন তিলাওয়াত - পারা ২৯ - সাউদ আল-শুরাইম')
        expected_title = "পারা ২৯ - সাউদ আল-শুরাইম - কুরআন তিলাওয়াত"
        self.assertEqual(lines[0], expected_title)
        
        # 2. Chapter Verification (Should fail - currently '01:23:20 Surah আল-মুলক')
        # Note: 'সুরা' vs 'সুরাহ' based on specs/conventions. Spec said 'সুরা' (e.g. '00:00 সুরা আল-ফাতিহা')
        chapter_line = lines[3] # Index 0: title, 1: desc, 2: 'Chapters:', 3: first chapter
        self.assertIn("সুরাহ আল-মুলক", chapter_line)
        self.assertIn("00:00", chapter_line)
        
        # Second chapter should be the Surah at its actual offset
        self.assertIn("01:05", lines[4])
        self.assertIn("সুরাহ আল-কলম", lines[4])

    def test_english_metadata_format(self):
        """
        Verify the English title and chapter labels.
        Expected Title: Juz 29 - Saud Al-Shuraym - Quran Recitation
        Expected Chapters: 00:00 Surah Al-Mulk, 01:05 Surah Al-Qalam
        """
        filename = generate_juz_details(
            juz_number=29, 
            reciter=self.reciter, 
            offsets=self.offsets, 
            language="english"
        )
        
        with open(filename, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            
        expected_title = "Juz 29 - Saud Al-Shuraym - Quran Recitation"
        self.assertEqual(lines[0], expected_title)
        self.assertIn("Surah Al-Mulk", lines[3])
        self.assertIn("00:00", lines[3])
        self.assertIn("Surah Al-Qalam", lines[4])
        self.assertIn("01:05", lines[4])

if __name__ == "__main__":
    unittest.main()
