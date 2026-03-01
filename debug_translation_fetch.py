from db_ops.crud_text import get_full_translation_for_ayah
from config_manager import config_manager

def debug_fetch():
    surah_number = 1
    ayah_number = 1
    
    # Check default language
    lang = config_manager.get("DEFAULT_LANGUAGE", "bengali")
    print(f"Default Language: {lang}")
    
    # Fetch translation
    text = get_full_translation_for_ayah(surah_number, ayah_number)
    print(f"Result for {surah_number}:{ayah_number}:")
    print(f"'{text}'")
    print(f"Type: {type(text)}")
    print(f"Length: {len(text)}")
    if text:
        print(f"Hex: {text.encode('utf-8').hex()}")

if __name__ == "__main__":
    debug_fetch()
