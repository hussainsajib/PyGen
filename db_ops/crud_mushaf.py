import sqlite3
import os
from typing import List, Dict

DB_15_LINES = "databases/text/qpc-v2-15-lines.db"
DB_WBW = "databases/text/word_by_word_qpc-v2.db" # Standard QPC v2 words

def get_surah_page_range(surah_number: int):
    """Returns (start_page, end_page) for a given surah."""
    conn = sqlite3.connect(DB_15_LINES)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(page_number), MAX(page_number) FROM pages WHERE surah_number = ?", (surah_number,))
        res = cursor.fetchone()
        if res and res[0] is not None:
            return res
            
        # Fallback: if surah_number is not explicitly set in the page headers (e.g. continuation)
        # We need to find pages where this surah's words exist.
        # This is slower but more accurate for edge cases.
        conn_wbw = sqlite3.connect(DB_WBW)
        cursor_wbw = conn_wbw.cursor()
        cursor_wbw.execute("SELECT MIN(id), MAX(id) FROM words WHERE surah = ?", (surah_number,))
        w_range = cursor_wbw.fetchone()
        if not w_range or w_range[0] is None:
            return (None, None)
            
        cursor.execute("SELECT MIN(page_number), MAX(page_number) FROM pages WHERE first_word_id <= ? AND last_word_id >= ?", (w_range[1], w_range[0]))
        return cursor.fetchone()
    finally:
        conn.close()

def get_juz_boundaries(juz_number: int):
    """
    Retrieves start and end boundaries for a Juz from the metadata database.
    Returns a dict with surah/ayah start/end, verse_mapping, and page range.
    """
    JUZ_DB = "databases/text/quran-metadata-juz.sqlite"
    conn = sqlite3.connect(JUZ_DB)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT first_verse_key, last_verse_key, verse_mapping FROM juz WHERE juz_number = ?", (juz_number,))
        row = cursor.fetchone()
        if row:
            import json
            first_v = row[0].split(":")
            last_v = row[1].split(":")
            mapping = json.loads(row[2])
            
            # Derive page range
            surahs = sorted([int(s) for s in mapping.keys()])
            start_p = get_surah_page_range(surahs[0])[0]
            end_p = get_surah_page_range(surahs[-1])[1]
            
            return {
                "start_surah": int(first_v[0]),
                "start_ayah": int(first_v[1]),
                "end_surah": int(last_v[0]),
                "end_ayah": int(last_v[1]),
                "verse_mapping": mapping,
                "start_page": start_p,
                "end_page": end_p
            }
        return None
    finally:
        conn.close()

def get_mushaf_page_data(page_number: int):
    """
    Retrieves the raw line and word data for a specific 15-line Mushaf page.
    """
    conn_15line = sqlite3.connect(DB_15_LINES)
    conn_wbw = sqlite3.connect(DB_WBW)
    
    lines_data = []
    
    try:
        cursor_15line = conn_15line.cursor()
        cursor_wbw = conn_wbw.cursor()
        
        # 1. Fetch lines for the page
        cursor_15line.execute("""
            SELECT page_number, line_number, line_type, is_centered, first_word_id, last_word_id, surah_number
            FROM pages
            WHERE page_number = ?
            ORDER BY line_number
        """, (page_number,))
        
        lines = cursor_15line.fetchall()
        
        last_known_surah = None
        for line in lines:
            page_num, line_num, l_type, centered, start_id, end_id, surah_num = line
            
            # Global Suppression: Surah 1 (Basmallah is Ayah 1) and Surah 9 (No Basmallah)
            if l_type == 'basmallah' and surah_num in [1, 9]:
                continue

            words = []
            if start_id != '' and end_id != '':
                # 2. Fetch words for this line
                cursor_wbw.execute("""
                    SELECT id, location, surah, ayah, word, text
                    FROM words
                    WHERE id BETWEEN ? AND ?
                    ORDER BY id
                """, (start_id, end_id))
                
                words_raw = cursor_wbw.fetchall()
                for w in words_raw:
                    words.append({
                        "id": w[0],
                        "location": w[1],
                        "surah": w[2],
                        "ayah": w[3],
                        "word": w[4],
                        "text": w[5]
                    })
            
            # Propagate surah_number for filtering accuracy
            resolved_surah = surah_num
            if not resolved_surah or resolved_surah == '':
                if words:
                    resolved_surah = words[0]["surah"]
                elif last_known_surah:
                    resolved_surah = last_known_surah
            
            last_known_surah = resolved_surah

            lines_data.append({
                "page_number": page_num,
                "line_number": line_num,
                "line_type": l_type,
                "is_centered": bool(centered),
                "surah_number": resolved_surah,
                "words": words
            })
            
    finally:
        conn_15line.close()
        conn_wbw.close()
        
    return lines_data

def get_mushaf_page_data_structured(page_number: int):
    """
    Retrieves the structured page data for the 15-line Mushaf layout, 
    with concatenated words for ayah lines.
    """
    conn_15line = sqlite3.connect(DB_15_LINES)
    conn_wbw = sqlite3.connect(DB_WBW)
    
    lines_data = []
    
    try:
        cursor_15line = conn_15line.cursor()
        cursor_wbw = conn_wbw.cursor()
        
        # 1. Fetch lines for the page
        cursor_15line.execute("""
            SELECT page_number, line_number, line_type, is_centered, first_word_id, last_word_id, surah_number
            FROM pages
            WHERE page_number = ?
            ORDER BY line_number
        """, (page_number,))
        
        lines = cursor_15line.fetchall()
        
        last_known_surah = None
        for line in lines:
            page_num, line_num, l_type, centered, start_id, end_id, surah_num = line
            
            # Global Suppression: Surah 1 (Basmallah is Ayah 1) and Surah 9 (No Basmallah)
            if l_type == 'basmallah' and surah_num in [1, 9]:
                continue

            concatenated_text = ""
            first_word_surah = None
            if l_type == 'ayah' and start_id is not None and end_id is not None and start_id != '' and end_id != '':
                cursor_wbw.execute("""
                    SELECT text, surah
                    FROM words
                    WHERE id BETWEEN ? AND ?
                    ORDER BY id
                """, (start_id, end_id))
                
                words_raw = cursor_wbw.fetchall()
                if words_raw:
                    concatenated_text = " ".join([w[0] for w in words_raw])
                    first_word_surah = words_raw[0][1]
            
            # Propagate surah_number
            resolved_surah = surah_num
            if not resolved_surah or resolved_surah == '':
                if first_word_surah:
                    resolved_surah = first_word_surah
                elif last_known_surah:
                    resolved_surah = last_known_surah
            
            last_known_surah = resolved_surah

            lines_data.append({
                "page_number": page_num,
                "line_number": line_num,
                "line_type": l_type,
                "is_centered": bool(centered),
                "surah_number": resolved_surah,
                "text": concatenated_text
            })
            
    finally:
        conn_15line.close()
        conn_wbw.close()
        
    return lines_data

def align_mushaf_lines_with_timestamps(page_data: list, wbw_timestamps: dict):
    """
    Calculates start and end timestamps for each Mushaf line based on word-level timing.
    Uses min start and max end of all timestamped words in the line to handle missing segments.
    """
    for line in page_data:
        words = line.get("words", [])
        if not words:
            line["start_ms"] = None
            line["end_ms"] = None
            continue
            
        valid_starts = []
        valid_ends = []
        
        for w in words:
            segments = wbw_timestamps.get(w["ayah"], [])
            for seg in segments:
                if seg[0] == w["word"]:
                    valid_starts.append(seg[1])
                    valid_ends.append(seg[2])
                    break
        
        if valid_starts:
            line["start_ms"] = min(valid_starts)
        else:
            line["start_ms"] = None
            
        if valid_ends:
            line["end_ms"] = max(valid_ends)
        else:
            line["end_ms"] = None
        
    return page_data

def align_mushaf_lines_with_juz_timestamps(page_data: list, wbw_timestamps: dict):
    """
    Variant of alignment that uses composite keys (surah:ayah) for Juz-based timing.
    """
    for line in page_data:
        words = line.get("words", [])
        if not words:
            line["start_ms"] = None
            line["end_ms"] = None
            continue
            
        valid_starts = []
        valid_ends = []
        
        for w in words:
            # Composite key: "surah:ayah"
            key = f"{w['surah']}:{w['ayah']}"
            segments = wbw_timestamps.get(key, [])
            for seg in segments:
                if seg[0] == w["word"]:
                    valid_starts.append(seg[1])
                    valid_ends.append(seg[2])
                    break
        
        if valid_starts:
            line["start_ms"] = min(valid_starts)
        else:
            line["start_ms"] = None
            
        if valid_ends:
            line["end_ms"] = max(valid_ends)
        else:
            line["end_ms"] = None
        
    return page_data

def group_mushaf_lines_into_scenes(all_lines: list, threshold: int = 3, max_lines: int = 15, defer_if_no_ayah: bool = False) -> list:
    if not all_lines:
        return []
        
    scenes = []
    current_scene = []
    
    # 1. Group lines by Mushaf Page
    pages = {}
    for line in all_lines:
        p_num = line.get('page_number') or line.get('page')
        if p_num not in pages:
            pages[p_num] = []
        pages[p_num].append(line)
        
    sorted_p_nums = sorted(pages.keys())
    
    # 2. Iterate through pages and apply threshold
    for i, p_num in enumerate(sorted_p_nums):
        page_lines = pages[p_num]
        
        if i == 0 and len(sorted_p_nums) > 1:
            has_ayah = any(l.get('line_type') == 'ayah' for l in page_lines)
            
            # Special logic for standalone videos: defer if 0 ayahs, otherwise DON'T defer even if below threshold
            if defer_if_no_ayah:
                if not has_ayah:
                    # Defer orphaned headers
                    current_scene.extend(page_lines)
                    continue
                else:
                    # Has ayah, don't defer even if < threshold (Override threshold)
                    pass
            elif len(page_lines) < threshold:
                # Standard threshold-based deferral (used for Juz or when defer_if_no_ayah is False)
                current_scene.extend(page_lines)
                continue
            
        # Standard chunking logic for the page
        # If we have deferred lines, prepend them to the first chunk of this page
        if current_scene:
            page_lines = current_scene + page_lines
            current_scene = []
            
        # Chunk into max_lines
        chunks = [page_lines[j:j + max_lines] for j in range(0, len(page_lines), max_lines)]
        scenes.extend(chunks)
        
    # Handling remaining deferred lines (Short Surah Protection)
    if current_scene:
        scenes.append(current_scene)
        
    return scenes
