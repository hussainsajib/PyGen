from fontTools.ttLib import TTFont
import os
import json

FONT_PATH = "QPC_V2_Font.ttf/QCF_SurahHeader_COLOR-Regular.ttf"

def generate_map():
    if not os.path.exists(FONT_PATH):
        return
        
    font = TTFont(FONT_PATH)
    glyph_names = font.getGlyphOrder()
    
    # Filter for uniXXXX names
    uni_glyphs = [g for g in glyph_names if g.startswith("uni")]
    
    # Convert uniXXXX to integer code
    pua_map = {}
    surah_count = 0
    for g in uni_glyphs:
        try:
            code_hex = g[3:]
            code = int(code_hex, 16)
            surah_count += 1
            pua_map[surah_count] = code
            if surah_count == 114:
                break
        except:
            continue
            
    print(json.dumps(pua_map))

if __name__ == "__main__":
    generate_map()
