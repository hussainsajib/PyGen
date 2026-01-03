import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from processes.Classes.surah import Surah
from processes.Classes.reciter import Reciter
from processes.description import generate_details

def verify():
    print("Verifying Metadata Generation...")
    
    # Ensure directory exists
    os.makedirs("exported_data/details", exist_ok=True)
    
    # Setup test data
    surah = Surah(1) # Al-Fatihah
    reciter = Reciter("ar.alafasy") # Mishary Rashid Alafasy
    
    # 1. Bengali Short Single Verse
    print("Generating Bengali Short (Single Verse)...")
    file1 = generate_details(surah, reciter, True, 1, 1, is_short=True, language="bengali")
    print(f"File created: {file1}")
    with open(file1, "r", encoding="utf-8") as f:
        print("--- Content ---")
        print(f.read())
        print("------------------------------")

    # 2. English Standard Range
    print("Generating English Standard (Range)...")
    file2 = generate_details(surah, reciter, True, 1, 7, is_short=False, language="english")
    print(f"File created: {file2}")
    with open(file2, "r", encoding="utf-8") as f:
        print("--- Content ---")
        print(f.read())
        print("------------------------------")

if __name__ == "__main__":
    verify()
