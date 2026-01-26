from fontTools.ttLib import TTFont
import os

FONT_PATH = "QPC_V2_Font.ttf/QCF_SurahHeader_COLOR-Regular.ttf"

def inspect_font():
    if not os.path.exists(FONT_PATH):
        print("Font not found")
        return
        
    font = TTFont(FONT_PATH)
    
    # 1. Check cmap (Unicode mappings)
    cmap = font.getBestCmap()
    print(f"Total Unicode mappings: {len(cmap)}")
    
    # Check for surah-related names in glyph list
    glyph_names = font.getGlyphOrder()
    print(f"Total glyphs: {len(glyph_names)}")
    
    # Print all glyph names
    print("Glyph names:", glyph_names)
        
    # 2. Check GSUB (Ligatures)
    if 'GSUB' in font:
        print("GSUB table found. Checking for ligatures...")
        gsub = font['GSUB'].table
        for lookup_index, lookup in enumerate(gsub.LookupList.Lookup):
            if lookup.LookupType == 4: # Ligature Substitution
                for subtable in lookup.SubTable:
                    for first_glyph, ligatures in subtable.ligatures.items():
                        for lig in ligatures:
                            # lig.Component is the rest of the string
                            # lig.Ligature is the resulting glyph name
                            # Join first_glyph and components
                            input_glyphs = [first_glyph] + lig.Component
                            # Try to find ASCII characters for these glyphs
                            input_str = ""
                            for g in input_glyphs:
                                if g in reverse_cmap:
                                    code = reverse_cmap[g]
                                    if 32 <= code <= 126:
                                        input_str += chr(code)
                                    else:
                                        input_str += f"<{hex(code)}>"
                                else:
                                    input_str += f"[{g}]"
                            
                            print(f"Ligature: '{input_str}' -> {lig.Ligature}")
                                
if __name__ == "__main__":
    inspect_font()
