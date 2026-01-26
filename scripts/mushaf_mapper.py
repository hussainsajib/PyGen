import sqlite3
import os
import json
from PIL import Image, ImageDraw, ImageFont

def get_page_content(page_number, db_15line_path, db_wbw_path):
    """
    Groups words from WBW DB based on line definitions in 15-Line DB for a given page.
    """
    conn_15line = sqlite3.connect(db_15line_path)
    conn_wbw = sqlite3.connect(db_wbw_path)
    
    lines_data = []
    
    try:
        cursor_15line = conn_15line.cursor()
        cursor_wbw = conn_wbw.cursor()
        
        # 1. Fetch all lines for the given page
        cursor_15line.execute("""
            SELECT page_number, line_number, line_type, is_centered, first_word_id, last_word_id, surah_number
            FROM pages
            WHERE page_number = ?
            ORDER BY line_number
        """, (page_number,))
        
        lines = cursor_15line.fetchall()
        
        for line in lines:
            page_num, line_num, l_type, centered, start_id, end_id, surah_num = line
            
            # Skip lines with no word IDs
            if start_id == '' or end_id == '':
                lines_data.append({
                    "page_number": page_num,
                    "line_number": line_num,
                    "line_type": l_type,
                    "is_centered": bool(centered),
                    "surah_number": surah_num,
                    "words": []
                })
                continue

            # 2. Fetch words for this line range
            cursor_wbw.execute("""
                SELECT id, location, surah, ayah, word, text
                FROM words
                WHERE id BETWEEN ? AND ?
                ORDER BY id
            """, (start_id, end_id))
            
            words_raw = cursor_wbw.fetchall()
            
            words = []
            for w in words_raw:
                words.append({
                    "id": w[0],
                    "location": w[1],
                    "surah": w[2],
                    "ayah": w[3],
                    "word": w[4],
                    "text": w[5]
                })
            
            lines_data.append({
                "page_number": page_num,
                "line_number": line_num,
                "line_type": l_type,
                "is_centered": bool(centered),
                "surah_number": surah_num,
                "words": words
            })
            
    finally:
        conn_15line.close()
        conn_wbw.close()
        
    return lines_data

def render_page_to_image(page_content, output_path, page_number):
    """
    Renders the mapped page content to an image using page-specific QPC v2 fonts.
    """
    width, height = 1200, 1600
    bg_color = (255, 255, 245) # Cream
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Resolve page-specific font
    font_folder = "QPC_V2_Font.ttf"
    font_file = f"p{page_number}.ttf"
    font_path = os.path.join(font_folder, font_file)
    
    if not os.path.exists(font_path):
        print(f"Error: Font file not found at {font_path}. Rendering will likely fail.")
        font = ImageFont.load_default()
    else:
        try:
            # QPC v2 fonts typically need a larger size for clarity
            font = ImageFont.truetype(font_path, 80)
            print(f"Using page font: {font_path}")
        except Exception as e:
            print(f"Error loading font {font_path}: {e}")
            font = ImageFont.load_default()

    margin_top = 150
    line_spacing = 90
    
    for line in page_content:
        line_num = line['line_number']
        
        # Collect words for this line
        words_text = [w['text'] for w in line['words']]
        
        # QPC v2 fonts render the glyphs correctly when mapped to the right Unicode points.
        # Since standard Pillow is LTR, and Mushaf is RTL, we must reverse the order of words
        # so the first word of the line appears on the right.
        words_text.reverse()
        
        text = " ".join(words_text)
        
        # Center alignment
        try:
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
        except:
            text_width = 0

        x = (width - text_width) / 2
        y = margin_top + (line_num - 1) * line_spacing
        
        draw.text((x, y), text, font=font, fill=(0, 0, 0))
        
    image.save(output_path)
    return output_path

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python mushaf_mapper.py <page_number> [output_image_path]")
        sys.exit(1)
        
    page_num = int(sys.argv[1])
    output_img = sys.argv[2] if len(sys.argv) > 2 else f"page_{page_num}.png"
    
    db_15 = "databases/text/qpc-v2-15-lines.db"
    db_wbw = "databases/text/word_by_word_qpc-v2.db"
    
    try:
        print(f"Mapping Page {page_num}...")
        content = get_page_content(page_num, db_15, db_wbw)
        
        # Image output
        render_page_to_image(content, output_img, page_num)
        print(f"Image saved to {output_img}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)