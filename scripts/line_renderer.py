import sqlite3
import os
import argparse
from PIL import Image, ImageDraw, ImageFont

def get_line_content(page_number, line_number, db_15line_path, db_wbw_path):
    """
    Fetches the specific words for a given page and line number.
    """
    conn_15line = sqlite3.connect(db_15line_path)
    conn_wbw = sqlite3.connect(db_wbw_path)
    
    words = []
    line_info = None
    
    try:
        cursor_15line = conn_15line.cursor()
        cursor_wbw = conn_wbw.cursor()
        
        # 1. Fetch line definition
        cursor_15line.execute("""
            SELECT page_number, line_number, line_type, first_word_id, last_word_id
            FROM pages
            WHERE page_number = ? AND line_number = ?
        """, (page_number, line_number))
        
        row = cursor_15line.fetchone()
        if not row:
            return None, None
            
        page_num, line_num, l_type, start_id, end_id = row
        line_info = {"page": page_num, "line": line_num, "type": l_type}
        
        if start_id == '' or end_id == '':
            return line_info, []

        # 2. Fetch words
        cursor_wbw.execute("""
            SELECT text FROM words
            WHERE id BETWEEN ? AND ?
            ORDER BY id
        """, (start_id, end_id))
        
        words = [r[0] for row in cursor_wbw.fetchall() for r in [row]]
            
    finally:
        conn_15line.close()
        conn_wbw.close()
        
    return line_info, words

def render_line_to_image(words, page_number, output_path):
    """
    Renders a single line of Arabic text to an image with dynamic sizing.
    """
    # Resolve font
    font_path = f"QPC_V2_Font.ttf/p{page_number}.ttf"
    font_size = 100
    if not os.path.exists(font_path):
        print(f"Warning: Font {font_path} not found. Using default.")
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(font_path, font_size)

    # Prepare text: Reverse words for RTL simulation
    words_rev = list(words)
    words_rev.reverse()
    text = "  ".join(words_rev)
    
    # Use a dummy image to calculate the bounding box
    dummy_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    bbox = dummy_draw.textbbox((0, 0), text, font=font)
    
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    # Create image with padding (50px on sides, 40px top/bottom)
    padding_x = 100
    padding_y = 80
    width = tw + padding_x
    height = th + padding_y
    
    bg_color = (255, 255, 245) # Cream
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Center alignment in the new dynamic canvas
    x = (width - tw) / 2 - bbox[0]
    y = (height - th) / 2 - bbox[1]
    
    draw.text((x, y), text, font=font, fill=(0, 0, 0))
    
    image.save(output_path)
    print(f"Saved line image to {output_path} (Size: {width}x{height})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render a specific Mushaf line to an image.")
    parser.add_argument("--page", type=int, required=True, help="Page number (1-604)")
    parser.add_argument("--line", type=int, required=True, help="Line number (1-15)")
    parser.add_argument("--output", type=str, default="line_output.png", help="Output filename")
    
    args = parser.parse_args()
    
    db_15 = "databases/text/qpc-v2-15-lines.db"
    db_wbw = "databases/text/word_by_word_qpc-v2.db"
    
    info, words = get_line_content(args.page, args.line, db_15, db_wbw)
    
    if not info:
        print(f"Error: Line {args.line} on Page {args.page} not found.")
    elif not words:
        print(f"Info: Line {args.line} on Page {args.page} exists but has no text (Type: {info['type']}).")
    else:
        print(f"Rendering {len(words)} words from Page {args.page} Line {args.line}...")
        render_line_to_image(words, args.page, args.output)
