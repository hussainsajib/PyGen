from db_ops.crud_wbw import get_wbw_text_for_ayah, get_wbw_translation_for_ayah
import os

print(f"Text: {get_wbw_text_for_ayah('databases/text/qpc-hafs-word-by-word.db', 1, 1)[:2]}")
print(f"Trans: {get_wbw_translation_for_ayah('databases/translation/bengali/bangali-word-by-word-translation.sqlite', 1, 1)[:2]}")
