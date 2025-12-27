import os
import pytest
from processes.youtube_utils import get_video_details

def test_get_video_details_parsing():
    # Create a dummy info file
    info_file = "test_metadata.txt"
    content = """Optimized Title - Surah Al-Fatihah - Ayah 1 to 7 - Mishary
    
This is a concise description.
It has multiple lines.

#Shorts #Quran

TAGS: Quran, Islam, Shorts, Mishary Alafasy
"""
    with open(info_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    try:
        title, description, tags = get_video_details(info_file)
        
        assert title == "Optimized Title - Surah Al-Fatihah - Ayah 1 to 7 - Mishary"
        assert "This is a concise description." in description
        assert "#Shorts" in description
        assert "TAGS:" not in description
        assert "Quran" in tags
        assert "Islam" in tags
        assert "Shorts" in tags
        assert "Mishary Alafasy" in tags
        
    finally:
        if os.path.exists(info_file):
            os.remove(info_file)

if __name__ == "__main__":
    test_get_video_details_parsing()
