from processes.description import generate_juz_details
from processes.Classes import Reciter
import os

def test_juz_metadata_bengali():
    # Simulate data for Juz 1
    juz_number = 1
    reciter = Reciter("ar.alafasy") # Mishari Al-Afasy
    offsets = {1: 0, 2: 300} # Surah 1 at 0s, Surah 2 at 300s
    
    # Generate details in Bengali
    filename = generate_juz_details(juz_number, reciter, offsets, language="bengali")
    
    print(f"Generated metadata file: {filename}")
    
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
        print("--- Content Start ---")
        print(content)
        print("--- Content End ---")
        
        # Basic checks
        assert "কুরআন তিলাওয়াত - পারা ১" in content
        assert "সম্পূর্ণ পারা ১ তিলাওয়াত" in content
        assert "#Para1" in content
        assert "পারা ১" in content
        assert "মিশারি আল-আফাসি" in content

if __name__ == "__main__":
    if not os.path.exists("exported_data/details"):
        os.makedirs("exported_data/details")
    test_juz_metadata_bengali()
    print("Verification successful!")
