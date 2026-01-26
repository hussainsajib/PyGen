import sqlite3
import os

def analyze_all_pages():
    db_15 = "databases/text/qpc-v2-15-lines.db"
    db_wbw = "databases/text/word_by_word_qpc-v2.db"
    
    conn_15line = sqlite3.connect(db_15)
    conn_wbw = sqlite3.connect(db_wbw_path := db_wbw)
    
    cursor_15line = conn_15line.cursor()
    cursor_wbw = conn_wbw.cursor()
    
    total_pages = 604
    missing_data = []
    line_type_counts = {}
    total_words_mapped = 0
    
    print(f"Starting full Quran analysis (604 pages)...")
    
    for page_num in range(1, total_pages + 1):
        cursor_15line.execute("""
            SELECT line_number, line_type, first_word_id, last_word_id
            FROM pages
            WHERE page_number = ?
            ORDER BY line_number
        """, (page_num,))
        
        lines = cursor_15line.fetchall()
        
        for line in lines:
            line_num, l_type, start_id, end_id = line
            
            # Statistics
            line_type_counts[l_type] = line_type_counts.get(l_type, 0) + 1
            
            if start_id != '' and end_id != '':
                # Verify words exist
                cursor_wbw.execute("SELECT COUNT(*) FROM words WHERE id BETWEEN ? AND ?", (start_id, end_id))
                count = cursor_wbw.fetchone()[0]
                
                expected_count = int(end_id) - int(start_id) + 1
                if count != expected_count:
                    missing_data.append({
                        "page": page_num,
                        "line": line_num,
                        "type": l_type,
                        "start_id": start_id,
                        "end_id": end_id,
                        "found": count,
                        "expected": expected_count
                    })
                
                total_words_mapped += count
            elif l_type == 'ayah' or l_type == 'bismillah':
                # These usually should have IDs
                missing_data.append({
                    "page": page_num,
                    "line": line_num,
                    "type": l_type,
                    "reason": "Missing IDs for text line"
                })

    conn_15line.close()
    conn_wbw.close()
    
    return {
        "line_types": line_type_counts,
        "total_words_mapped": total_words_mapped,
        "anomalies": missing_data
    }

if __name__ == "__main__":
    results = analyze_all_pages()
    
    print("\n--- Analysis Results ---")
    print(f"Total words successfully mapped: {results['total_words_mapped']}")
    print("\nLine Type Distribution:")
    for ltype, count in results['line_types'].items():
        print(f"  - {ltype}: {count}")
        
    print(f"\nTotal Anomalies Found: {len(results['anomalies'])}")
    if results['anomalies']:
        print("\nTop 10 Anomalies:")
        for a in results['anomalies'][:10]:
            print(f"  - Page {a['page']} Line {a['line']} ({a['type']}): {a.get('reason', f'Found {a.get("found")} of {a.get("expected")}')}")
    else:
        print("\nSUCCESS: All text-bearing lines mapped perfectly to WBW database.")
