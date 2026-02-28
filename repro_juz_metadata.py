import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from processes.Classes import Reciter, Surah
from processes.description import generate_juz_details

def repro():
    # Use a real reciter
    reciter = Reciter("ar.saoodshuraym")
    
    # Mock Offsets in MS (as passed by mushaf_video.py)
    offsets_ms = {
        1: 5000,   # 5s
        2: 65000   # 1m 5s
    }
    
    print("--- Current Metadata (Bengali) ---")
    filename = generate_juz_details(juz_number=29, reciter=reciter, offsets=offsets_ms, language="bengali")
    with open(filename, "r", encoding="utf-8") as f:
        print(f.read())
        
    print("\n--- Current Metadata (English) ---")
    filename = generate_juz_details(juz_number=29, reciter=reciter, offsets=offsets_ms, language="english")
    with open(filename, "r", encoding="utf-8") as f:
        print(f.read())

if __name__ == "__main__":
    repro()
